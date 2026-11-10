__all__ = (
    "TextEncodingManager",
)

_TextEncodingManager = None

def _allocate():
    global _allocate
    global _TextEncodingManager

    class __TextEncodingManager:
        __slots__ = (
            "_selected_encoding",
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
        def selected_encoding(self):
            return self._selected_encoding

        @selected_encoding.setter
        def selected_encoding(self, value):
            self._selected_encoding = value

        def construct(self):
            self._selected_encoding = "utf-8"
            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True


    _TextEncodingManager = __TextEncodingManager
    _allocate = lambda: None


def TextEncodingManager():
    if _TextEncodingManager is None:
        _allocate()

    return _TextEncodingManager


# TextEncodingManager()
