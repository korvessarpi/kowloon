class _LazyCreate:
    def __getattr__(self, name):
        # Import only when accessed (after Django apps are ready)
        from world.evennia_lazy import create as real_create
        return getattr(real_create, name)

# Expose `create` with the same attribute API as evennia.utils.create
create = _LazyCreate()
