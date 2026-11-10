__all__ = (
    "JsonFileIoManager",
)

_json = None
_pathlib = None
_JsonManager = None
_TextEncodingManager = None
_JsonFileIoManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _JsonFileIoManager

    class __JsonFileIoManager:
        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _ExternalDependencyManager
            global _json
            global _pathlib
            global _JsonManager
            global _TextEncodingManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _json = (
                _ExternalDependencyManager().import_module(
                    path="json",
                )
            )
            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
                )
            )
            _JsonManager = (
                _ExternalDependencyManager().import_module(
                    path=".json_manager",
                    package="qlogicae_cor.v3.library",
                    member="JsonManager",
                    is_member_callable=True,
                )
            )
            _TextEncodingManager = (
                _ExternalDependencyManager().import_module(
                    path=".text_encoding_manager",
                    package="qlogicae_cor.v3.library",
                    member="TextEncodingManager",
                    is_member_callable=True,
                )
            )
            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def read_file(self, file_path):
            path = _pathlib().Path(file_path)

            output_data = {}

            with path.open(
                mode="r",
                encoding=_TextEncodingManager().get_singleton().selected_encoding,
            ) as file:
                output_data = _json().load(file) or {}

            return output_data

        def write_file(self, file_path, data):
            path = _pathlib().Path(file_path)

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with path.open(
                mode="w",
                encoding=_TextEncodingManager().get_singleton().selected_encoding,
            ) as file:
                _json().dump(
                    data,
                    file,
                    indent=_JsonManager().get_singleton().indent_count,
                    ensure_ascii=_JsonManager().get_singleton().is_ascii_format_enabled,
                    sort_keys=_JsonManager().get_singleton().is_key_sortable,
                )

            return True

    _JsonFileIoManager = __JsonFileIoManager
    _allocate = lambda: None


def JsonFileIoManager():
    if _JsonFileIoManager is None:
        _allocate()

    return _JsonFileIoManager


# JsonFileIoManager()
