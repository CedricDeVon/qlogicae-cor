__all__ = (
    "PythonRuntimeUtilityManager",
)

_PythonRuntimeUtilityManager = None


def _allocate_module():
    global _allocate_module
    global _PythonRuntimeUtilityManager

    class __PythonRuntimeUtilityManager:
        __slots__ = (
            "_is_allocated_during_object_construction"
        )

        _singleton = None

        def __init__(self):
            self.construct()

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @property
        def is_allocated_during_object_construction(self):
            return self._is_allocated_during_object_construction

        @is_allocated_during_object_construction.setter
        def is_allocated_during_object_construction(self, value):
            self._is_allocated_during_object_construction = value

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            self._is_allocated_during_object_construction = False

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True


    _PythonRuntimeUtilityManager = __PythonRuntimeUtilityManager
    _allocate_module = lambda: None


def PythonRuntimeUtilityManager():
    if _PythonRuntimeUtilityManager is None:
        _allocate_module()

    return _PythonRuntimeUtilityManager


# PythonRuntimeUtilityManager()
