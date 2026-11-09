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

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )
            _PluginManager = (
                _ExternalDependencyManager().import_module(
                    path=".plugin_manager",
                    package="qlogicae_cor.v3.library",
                    member="PluginManager",
                    is_member_callable=True,
                )
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError("'kwargs' must be a dictionary")

            plugin_manager = (
                _PluginManager().get_singleton()
            )
            plugin_manager.setup(
                **kwargs
            )

            return True

        def shutdown(self):
            return True

        def read_module_exports(self):
            plugin_manager = (
                _PluginManager()
                    .get_singleton()
            )

            data = (
                plugin_manager.module_exports or {}
            )

            return data


    _CliPluginManager = __CliPluginManager
    _allocate = lambda: None


def CliPluginManager():
    if _CliPluginManager is None:
        _allocate()

    return _CliPluginManager



# CliPluginManager()
