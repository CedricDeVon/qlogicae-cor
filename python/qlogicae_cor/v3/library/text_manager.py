__all__ = (
    "TextManager",
)

_TextManager = None


def _allocate_module():
    global _allocate_module
    global _TextManager

    class __TextManager:
        __slots__ = (
            "_valid_file_extensions",
        )

        _singleton = None

        def __init__(self):
            self._valid_file_extensions = {".txt"}

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def valid_file_extensions(self):
            return self._valid_file_extensions

        def is_valid(self, file_path):
            if file_path.suffix.lower() not in self.valid_file_extensions:
                return False

            return True

    _TextManager = __TextManager
    _allocate_module = lambda: None


def TextManager():
    if _TextManager is None:
        _allocate_module()

    return _TextManager


TextManager()
