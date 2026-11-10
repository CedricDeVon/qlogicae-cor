__all__ = (
    "JsonManager",
)

_pathlib = None
_JsonManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _JsonManager

    class __JsonManager:
        __slots__ = (
            "_valid_file_extensions",
            "_is_ascii_format_enabled",
            "_indent_count",
            "_is_key_sortable",
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

        def is_valid(
            self,
            file_pathlib,
        ):
            path = _pathlib().Path(file_pathlib)

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

        def construct(self):
            global _ExternalDependencyManager
            global _pathlib

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
                )
            )


            self._valid_file_extensions = {
                ".json",
            }
            self._is_ascii_format_enabled = False
            self._indent_count = 4
            self._is_key_sortable = False

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True


    _JsonManager = __JsonManager
    _allocate = lambda: None


def JsonManager():
    if _JsonManager is None:
        _allocate()

    return _JsonManager


# JsonManager()
