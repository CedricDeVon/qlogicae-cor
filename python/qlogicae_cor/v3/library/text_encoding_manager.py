__all__ = (
    "TextEncodingManager",
)

_TextEncodingManager = None

def _allocate_module():
    global _allocate_module
    global _TextEncodingManager

    class __TextEncodingManager:
        __slots__ = (
            "_selected_encoding",
        )

        _singleton = None

        def __init__(self):
            self._selected_encoding = "utf-8"

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

    _TextEncodingManager = __TextEncodingManager
    _allocate_module = lambda: None


def TextEncodingManager():
    if _TextEncodingManager is None:
        _allocate_module()

    return _TextEncodingManager


# TextEncodingManager()
