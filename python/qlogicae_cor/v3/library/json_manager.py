__all__ = (
    "JsonManager",
)

_Path = None
_JsonManager = None


def _allocate_module():
    global _allocate_module
    global _Path
    global _JsonManager

    from pathlib import Path

    _Path = Path

    class __JsonManager:
        __slots__ = (
            "_valid_file_extensions",
            "_is_ascii_format_enabled",
            "_indent_count",
            "_is_key_sortable",
        )

        _singleton = None

        def __init__(self):
            self._valid_file_extensions = {
                ".json",
            }
            self._is_ascii_format_enabled = False
            self._indent_count = 4
            self._is_key_sortable = False

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def valid_file_extensions(self):
            return self._valid_file_extensions

        def is_valid(
            self,
            file_path,
        ):
            path = _Path(file_path)

            return (
                path.suffix.lower()
                in self.valid_file_extensions
            )

        @property
        def is_ascii_format_enabled(self):
            return self._is_ascii_format_enabled

        @is_ascii_format_enabled.setter
        def is_ascii_format_enabled(
            self,
            value,
        ):
            self._is_ascii_format_enabled = value

        @property
        def indent_count(self):
            return self._indent_count

        @indent_count.setter
        def indent_count(
            self,
            value,
        ):
            if value < 0:
                raise ValueError(
                    "indent_count must be non-negative.",
                )

            self._indent_count = value

        @property
        def is_key_sortable(self):
            return self._is_key_sortable

        @is_key_sortable.setter
        def is_key_sortable(
            self,
            value,
        ):
            self._is_key_sortable = value

    _JsonManager = __JsonManager
    _allocate_module = lambda: None


def JsonManager():
    if _JsonManager is None:
        _allocate_module()

    return _JsonManager


# JsonManager()
