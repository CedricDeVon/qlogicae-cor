__all__ = (
    "FileIoManager",
)

_Path = None
_PythonRuntimeUtilityManager = None
_TextEncodingManager = None
_FileIoManager = None


def _allocate():
    global _allocate
    global _FileIoManager

    class __FileIoManager:
        _singleton = None

        def __init__(self):
            self.construct()

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _Path
            global _PythonRuntimeUtilityManager
            global _TextEncodingManager

            from pathlib import Path

            from .python_runtime_utility_manager import PythonRuntimeUtilityManager
            from .text_encoding_manager import TextEncodingManager

            _Path = Path
            _PythonRuntimeUtilityManager = (
                PythonRuntimeUtilityManager().get_singleton
            )
            _TextEncodingManager = TextEncodingManager().get_singleton

            if _PythonRuntimeUtilityManager().is_allocated_during_object_construction:
                _TextEncodingManager()

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True

        def read_file(self, file_path):
            path = _Path(file_path)

            with path.open(
                mode="r",
                encoding=_TextEncodingManager().selected_encoding,
            ) as file:
                return file.read() or ""

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
                file.write(str(data))

            return True

    _FileIoManager = __FileIoManager
    _allocate = lambda: None


def FileIoManager():
    if _FileIoManager is None:
        _allocate()

    return _FileIoManager


# FileIoManager()
