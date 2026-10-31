__all__ = (
    "SingletonManager",
)

_SingletonManager = None


def _allocate_module():
    global _allocate_module
    global _SingletonManager

    class __SingletonManager:
        _singletons = {}
        _singleton_arrays = {}

        @classmethod
        def reset(cls):
            cls._singletons.clear()
            cls._singleton_arrays.clear()

            return True

        @classmethod
        def get_singleton(cls, constructor):
            instance = cls._singletons.get(constructor)

            if instance is None:
                instance = constructor()
                cls._singletons[constructor] = instance

            return instance

        @classmethod
        def get_singleton_from_pool(
            cls,
            constructor,
            instance_count,
            index,
        ):
            if instance_count <= 0:
                raise ValueError("something went wrong here")

            instances = cls._singleton_arrays.get(constructor)

            if instances is None:
                instances = [
                    constructor()
                    for _ in range(instance_count)
                ]

                cls._singleton_arrays[constructor] = instances

            return instances[abs(index) % instance_count]

    _SingletonManager = __SingletonManager
    _allocate_module = lambda: None


def SingletonManager():
    if _SingletonManager is None:
        _allocate_module()

    return _SingletonManager


# SingletonManager()
# Refactor while following the format above.
# Imports must be within the _handle_dynamic_import() method.
# Remove all type annotations.
# use 'is_allocated_during_object_construction'
# PythonRuntimeUtilityManager must include _PythonRuntimeUtilityManager

