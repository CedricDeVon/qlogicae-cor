__all__ = (
    "TextManager",
)

_TextManager = None


def _allocate():
    global _allocate
    global _TextManager

    class __TextManager:
        __slots__ = (
            "_valid_file_extensions",
        )

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

        @property
        def valid_file_extensions(self):
            return self._valid_file_extensions

        def construct(self):
            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            self._valid_file_extensions = {".txt"}

            return True

        def is_valid(self, file_path):
            if file_path.suffix.lower() not in self.valid_file_extensions:
                return False

            return True

    _TextManager = __TextManager
    _allocate = lambda: None


def TextManager():
    if _TextManager is None:
        _allocate()

    return _TextManager


# TextManager()
