__all__ = (
    "JsonTextManager",
)

_json = None
_JsonManager = None
_JsonTextManager = None
_PythonRuntimeUtilityManager = None


def _allocate_module():
    global _allocate_module
    global _json
    global _JsonManager
    global _JsonTextManager
    global _PythonRuntimeUtilityManager

    import json

    from .json_manager import JsonManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager

    _json = json
    _JsonManager = JsonManager().get_singleton
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()

    class __JsonTextManager:
        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _JsonManager()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def is_valid(self, value):
            _json.loads(value)

            return True

        def convert_to_object(self, value):
            return _json.loads(value)

        def convert_to_string(self, value):
            result = _json.dumps(
                value,
                indent=_JsonManager().indent_count,
                ensure_ascii=_JsonManager().is_ascii_format_enabled,
            )

            return result

    _JsonTextManager = __JsonTextManager
    _allocate_module = lambda: None


def JsonTextManager():
    if _JsonTextManager is None:
        _allocate_module()

    return _JsonTextManager


# JsonTextManager()
