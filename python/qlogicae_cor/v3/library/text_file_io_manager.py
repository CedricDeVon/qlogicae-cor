__all__ = (
    "TextFileIoManager",
)

_pathlib = None
_TextEncodingManager = None
_TextFileIoManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _TextFileIoManager

    class __TextFileIoManager:
        __slots__ = ()

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

        def read_file(self, file_path):
            path = _pathlib().Path(file_path)

            output_data = ""

            with path.open(
                mode="r",
                encoding=_TextEncodingManager().selected_encoding,
            ) as file:
                output_data = file.read() or ""

            return output_data

        def construct(self):
            global _pathlib
            global _TextEncodingManager
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
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

        def write_file(self, file_path, data):
            path = _pathlib().Path(file_path)

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with path.open(
                mode="w",
                encoding=_TextEncodingManager().selected_encoding,
            ) as file:
                file.write(str(data))

            return True

    _TextFileIoManager = __TextFileIoManager
    _allocate = lambda: None


def TextFileIoManager():
    if _TextFileIoManager is None:
        _allocate()

    return _TextFileIoManager


# TextFileIoManager()
