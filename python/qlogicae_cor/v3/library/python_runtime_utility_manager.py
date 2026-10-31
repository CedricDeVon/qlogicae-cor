__all__ = (
    "PythonRuntimeUtilityManager",
)

_PythonRuntimeUtilityManager = None


def _allocate_module():
    global _allocate_module
    global _PythonRuntimeUtilityManager

    class __PythonRuntimeUtilityManager:
        is_allocated_during_object_construction = False

        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

    _PythonRuntimeUtilityManager = __PythonRuntimeUtilityManager
    _allocate_module = lambda: None


def PythonRuntimeUtilityManager():
    if _PythonRuntimeUtilityManager is None:
        _allocate_module()

    return _PythonRuntimeUtilityManager


# PythonRuntimeUtilityManager()
