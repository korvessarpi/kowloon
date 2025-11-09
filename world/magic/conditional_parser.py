import re
from typing import Dict, List, Tuple, Callable, Any

from django.conf import settings
from evennia.utils import utils, logger
from django.utils.translation import gettext as _  # Django 4+

__all__ = ("ConditionalHandler", "ConditionalException")

WARNING_LOG = getattr(settings, "LOCKWARNING_LOG_FILE", None)
_MAGIC_CONDITION_FUNCS: Dict[str, Callable[..., Any]] = {}

# Pre-compiled regular expressions
# Function calls like: func(arg1, arg2=val, ...)
_RE_FUNCS = re.compile(r"\w+\([^)]*\)")
# Only allow placeholders and boolean operators in the final eval string.
# We intentionally permit the literal '%s' placeholder produced during parsing.
_RE_OK = re.compile(r"%s|and|or|not")


class ConditionalException(Exception):
    """Raised when a conditional expression is malformed or references unknown functions."""
    pass


def _cache_conditionfuncs() -> None:
    """
    Load/refresh the condition function registry from modules listed in
    settings.MAGIC_CONDITION_MODULES. Each module is scanned for callables.
    """
    global _MAGIC_CONDITION_FUNCS
    _MAGIC_CONDITION_FUNCS = {}
    for modulepath in getattr(settings, "MAGIC_CONDITION_MODULES", []):
        _MAGIC_CONDITION_FUNCS.update(utils.callables_from_module(modulepath))


class ConditionalHandler:
    """
    Parses and evaluates conditional expressions stored in a compact string form.

    The storage string format is a semicolon-separated list of rules:
        "<access_type>: <func1(args)> AND/OR/NOT <func2(args)> ...; <access_type2>: ..."

    Example:
        "cast: has_mana(10) AND knows_spell(name='firebolt'); reveal: is_friend(target)"

    Each function referenced must exist in one of the modules listed in
    settings.MAGIC_CONDITION_MODULES.
    """

    def __init__(self, condition_storagestring: str):
        if not _MAGIC_CONDITION_FUNCS:
            _cache_conditionfuncs()

        self.conditions: Dict[str, Tuple[str, Tuple[Tuple[Callable, list, dict], ...], str]] = (
            self._parse_conditional_string(condition_storagestring)
        )
        self.raw_string = condition_storagestring

    @staticmethod
    def _parse_conditional_string(storage_conditionstring: str):
        """
        Parse storage string into a dict:
            { access_type: (eval_format_string, tuple((func, args, kwargs)), original_raw) }
        """
        conditions: Dict[str, Tuple[str, Tuple[Tuple[Callable, list, dict], ...], str]] = {}
        if not storage_conditionstring:
            return conditions

        elist: List[str] = []  # errors to raise
        wlist: List[str] = []  # warnings to log

        for raw_condition in storage_conditionstring.split(";"):
            raw_condition = raw_condition.strip()
            if not raw_condition:
                continue

            try:
                access_type, rhs = (part.strip() for part in raw_condition.split(":", 1))
            except ValueError:
                # malformed ("no ':'")
                logger.log_trace()
                return conditions

            # Extract function calls and build an eval-able format string consisting of
            # '%s' placeholders and the operators 'and', 'or', 'not'
            funclist = _RE_FUNCS.findall(rhs)
            evalstring = rhs
            for pattern in ("AND", "OR", "NOT"):
                evalstring = re.sub(rf"\b{pattern}\b", pattern.lower(), evalstring)

            condition_funcs: List[Tuple[Callable, list, dict]] = []
            nfuncs = len(funclist)

            for funcstring in funclist:
                # Split "func(a, b=1)" -> funcname="func", rest="a, b=1"
                try:
                    funcname, rest = (part.strip().strip(")") for part in funcstring.split("(", 1))
                except ValueError:
                    elist.append(_("Condition: malformed function call '%s'.") % funcstring)
                    continue

                func = _MAGIC_CONDITION_FUNCS.get(funcname)
                if not callable(func):
                    elist.append(_("Condition: magic condition-function '%s' is not available.") % funcstring)
                    continue

                # Parse args/kwargs from "a, b=1, c='x'"
                raw_parts = [p.strip() for p in rest.split(",")] if rest else []
                args = [p for p in raw_parts if p and "=" not in p]
                kwargs_pairs = [p for p in raw_parts if p and "=" in p]
                kwargs = {}
                for pair in kwargs_pairs:
                    k, v = pair.split("=", 1)
                    kwargs[k.strip()] = eval(v, {}, {}) if v else None  # allow simple literals

                condition_funcs.append((func, args, kwargs))
                # Replace this function invocation with '%s' placeholder in eval format string
                evalstring = evalstring.replace(funcstring, "%s", 1)

            # If any function failed to resolve, skip this rule (errors will be raised after loop)
            if len(condition_funcs) < nfuncs:
                continue

            try:
                # Reduce evalstring to a safe boolean skeleton (placeholders + boolean ops only)
                safe_evalstring = " ".join(_RE_OK.findall(evalstring))
                # Sanity-check the skeleton by trying to evaluate with True placeholders
                test_tuple = tuple(True for _ in funclist)
                eval(safe_evalstring % test_tuple, {}, {})
            except Exception:
                elist.append(_("Condition: definition '%s' has syntax errors.") % raw_condition)
                continue

            # Record (warn if duplicate access_type)
            if access_type in conditions:
                wlist.append(
                    _(
                        "ConditionalHandler: access type '%(access_type)s' changed from "
                        "'%(source)s' to '%(goal)s'"
                    )
                    % {
                        "access_type": access_type,
                        "source": conditions[access_type][2],
                        "goal": raw_condition,
                    }
                )

            conditions[access_type] = (
                safe_evalstring,
                tuple(condition_funcs),
                raw_condition,
            )

        if wlist and WARNING_LOG:
            logger.log_file("\n".join(wlist), WARNING_LOG)
        if elist:
            # Bubble all parse/link errors at once
            raise ConditionalException("\n".join(elist))

        return conditions

    def check(self, caster: Any, target: Any, access_type: str, default: bool = False) -> bool:
        """
        Evaluate a stored conditional by access_type. Returns `default` if that type is not defined.
        """
        if access_type not in self.conditions:
            return default

        evalstring, func_tup, _raw = self.conditions[access_type]

        # Execute functions in stored order, building a tuple of booleans
        true_false = tuple(bool(func(caster, target, *args, **kwargs)) for func, args, kwargs in func_tup)

        # Evaluate the boolean skeleton with results plugged into '%s' slots.
        return bool(eval(evalstring % true_false, {}, {}))

    def __str__(self) -> str:
        return self.raw_string or ""

