__all__ = (
    "CliPluginManager",
)

_PluginManager = None
_CliPluginManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _CliPluginManager

    class __CliPluginManager:
        __slots__ = ()

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
            global _PluginManager
            global _ExternalDependencyManager

            from .plugin_manager import PluginManager

            _PluginManager = PluginManager().get_singleton

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True

        def read_root_data(self):
            plugin_manager = (
                _PluginManager()
            )

            data = (
                (plugin_manager.collection or {}).get(
                    "cli", {}
                ) or {}
            )

            return data


    _CliPluginManager = __CliPluginManager
    _allocate = lambda: None


def CliPluginManager():
    if _CliPluginManager is None:
        _allocate()

    return _CliPluginManager
