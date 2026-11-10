__all__ = (
    "JsonTextManager",
)

_json = None
_JsonManager = None
_JsonTextManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _JsonTextManager

    class __JsonTextManager:
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
            global _json
            global _JsonManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _json = (
                _ExternalDependencyManager().import_module(
                    path="json",
                )
            )
            _JsonManager = (
                _ExternalDependencyManager().import_module(
                    path=".json_manager",
                    package="qlogicae_cor.v3.library",
                    member="JsonManager",
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

        def is_valid(self, value):
            _json().loads(value)

            return True

        def convert_to_object(self, value):
            return _json().loads(value)

        def convert_to_string(self, value):
            result = _json().dumps(
                value,
                indent=_JsonManager().get_singleton().indent_count,
                ensure_ascii=_JsonManager().get_singleton().is_ascii_format_enabled,
            )

            return result

    _JsonTextManager = __JsonTextManager
    _allocate = lambda: None


def JsonTextManager():
    if _JsonTextManager is None:
        _allocate()

    return _JsonTextManager


# JsonTextManager()
