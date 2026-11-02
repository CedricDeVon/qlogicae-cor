__all__ = (
    "TextFileIoManager",
)

_pathlib = None
_PythonRuntimeUtilityManager = None
_TextEncodingManager = None
_TextFileIoManager = None


def _allocate_module():
    global _allocate_module
    global _TextFileIoManager

    class __TextFileIoManager:
        __slots__ = ()

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

        def read_file(self, file_path):
            path = _pathlib.Path(file_path)

            output_data = ""

            with path.open(
                mode="r",
                encoding=_TextEncodingManager().selected_encoding,
            ) as file:
                output_data = file.read() or ""

            return output_data

        def construct(self):
            global _pathlib
            global _PythonRuntimeUtilityManager
            global _TextEncodingManager

            import pathlib

            from .python_runtime_utility_manager import PythonRuntimeUtilityManager
            from .text_encoding_manager import TextEncodingManager

            _pathlib = pathlib
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

        def write_file(self, file_path, data):
            path = _pathlib.Path(file_path)

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
    _allocate_module = lambda: None


def TextFileIoManager():
    if _TextFileIoManager is None:
        _allocate_module()

    return _TextFileIoManager


# TextFileIoManager()
