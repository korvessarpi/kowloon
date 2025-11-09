from __future__ import annotations

def get_channelhandler():
    try:
        from evennia.comms.channel import CHANNEL_HANDLER  # new path
        return CHANNEL_HANDLER
    except Exception:
        pass
    try:
        from evennia.comms.channelhandler import CHANNELHANDLER as CH  # old path
        return CH
    except Exception:
        pass
    class _Stub:
        def __getattr__(self, name):
            raise RuntimeError("Channel system unavailable in this Evennia version (compat stub).")
    return _Stub()

def get_cmd(name: str):
    for modpath in (
        "evennia.commands.default.comms",
        "evennia.commands.default.general",
        "evennia.commands.default.system",
    ):
        try:
            mod = __import__(modpath, fromlist=[name])
            if hasattr(mod, name):
                return getattr(mod, name)
        except Exception:
            pass
    try:
        from evennia.commands.command import Command  # type: ignore
    except Exception:
        class Command:  # type: ignore
            key = "disabled"
            locks = "cmd:all()"
            help_category = "General"
            def func(self):
                self.caller.msg("Command disabled.")
    class DisabledCmd(Command):  # type: ignore
        key = (name or "disabled").lower()
        locks = "cmd:all()"
        help_category = "General"
        def func(self):
            self.caller.msg(f"{name} is unavailable (Evennia API changed).")
    return DisabledCmd


# --- Compatibility shims for legacy commands ---

def get_cmd_cdestroy():
    """
    Return a stub for the legacy @cdestroy command (removed/renamed in newer trees).
    This prevents import errors while keeping the command disabled by default.
    """
    try:
        from evennia.commands.command import Command
    except Exception:
        # Minimal fallback if import path changes; this should never happen in normal runs.
        class Command(object):
            key = ""
            aliases = []
            locks = ""
            help_category = ""
            def __init__(self, *a, **kw): pass
            def func(self): pass

    class CmdCDestroyStub(Command):
        key = "@cdestroy"
        aliases = []
        # restrict heavily; only devs can see/run, and it just prints a notice
        locks = "cmd:perm(Developers)"
        help_category = "Admin"

        def func(self):
            self.caller.msg("(@cdestroy is disabled in this build — shim provided by evennia_compat.)")

    return CmdCDestroyStub
