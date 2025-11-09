"""
Evennia 3 compatibility for legacy channel subcommands.
- On Evennia <3: re-export real commands from evennia.commands.default.comms
- On Evennia 3: provide harmless stubs for any missing CmdC* names.
"""
try:
    from evennia.commands.default import comms as _default_comms  # pre-v3
except Exception:
    _default_comms = None

def __getattr__(name):
    if _default_comms is not None and hasattr(_default_comms, name):
        return getattr(_default_comms, name)
    if name.startswith("CmdC"):
        class _Stub:
            key = name.replace("CmdC", "").lower() or "channel"
            def __init__(self, *a, **kw): pass
            def func(self, *a, **kw):
                try:
                    self.caller.msg(
                        f"Legacy channel subcommand '{name}' was removed in Evennia 3. "
                        "Use the unified 'channel' command (see 'help channel')."
                    )
                except Exception:
                    pass
        _Stub.__name__ = name
        return _Stub
    raise AttributeError(name)
