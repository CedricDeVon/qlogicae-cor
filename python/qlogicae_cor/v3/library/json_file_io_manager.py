__all__ = (
    "JsonFileIoManager",
)

_json = None
_Path = None
_PythonRuntimeUtilityManager = None
_JsonManager = None
_TextEncodingManager = None
_JsonFileIoManager = None


def _allocate_module():
    global _allocate_module
    global _json
    global _Path
    global _PythonRuntimeUtilityManager
    global _JsonManager
    global _TextEncodingManager
    global _JsonFileIoManager

    import json
    from pathlib import Path

    from .json_manager import JsonManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .text_encoding_manager import TextEncodingManager

    _json = json
    _Path = Path
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _JsonManager = JsonManager().get_singleton
    _TextEncodingManager = TextEncodingManager().get_singleton

    class __JsonFileIoManager:
        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _JsonManager()
                _TextEncodingManager()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def read_file(self, file_path):
            path = _Path(file_path)

            output_data = {}

            with path.open(
                mode="r",
                encoding=_TextEncodingManager().selected_encoding,
            ) as file:
                output_data = _json.load(file) or {}

            return output_data

        def write_file(self, file_path, data):
            path = _Path(file_path)

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with path.open(
                mode="w",
                encoding=_TextEncodingManager().selected_encoding,
            ) as file:
                _json.dump(
                    data,
                    file,
                    indent=_JsonManager().indent_count,
                    ensure_ascii=_JsonManager().is_ascii_format_enabled,
                    sort_keys=_JsonManager().is_key_sortable,
                )

            return True

    _JsonFileIoManager = __JsonFileIoManager
    _allocate_module = lambda: None


def JsonFileIoManager():
    if _JsonFileIoManager is None:
        _allocate_module()

    return _JsonFileIoManager


# JsonFileIoManager()
