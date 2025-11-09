"""Lazy wrappers for evennia.utils.create to avoid AppRegistryNotReady during import."""
def _real():
    from evennia.utils import create as _c
    return _c

class _CreateProxy:
    def __getattr__(self, name):
        return getattr(_real(), name)

create = _CreateProxy()

def create_object(*a, **k): return _real().create_object(*a, **k)
def create_script(*a, **k): return _real().create_script(*a, **k)
def create_channel(*a, **k): return _real().create_channel(*a, **k)
def create_help_entry(*a, **k): return _real().create_help_entry(*a, **k)
