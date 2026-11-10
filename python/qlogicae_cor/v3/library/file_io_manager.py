__all__ = (
    "FileIoManager",
)

_pathlib = None
_TextEncodingManager = None
_FileIoManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _FileIoManager

    class __FileIoManager:
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
            global _pathlib
            global _TextEncodingManager

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

        def read_file(self, file_path):
            path = _pathlib().Path(file_path)

            with path.open(
                mode="r",
                encoding=_TextEncodingManager().get_singleton().selected_encoding,
            ) as file:
                return file.read() or ""

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
                file.write(str(data))

            return True

    _FileIoManager = __FileIoManager
    _allocate = lambda: None


def FileIoManager():
    if _FileIoManager is None:
        _allocate()

    return _FileIoManager


# FileIoManager()
