__all__ = (
    "CliDisplayManager",
)

_CliPluginManager = None
_CliDisplayManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _CliDisplayManager

    class __CliDisplayManager:
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
            global _CliPluginManager
            global _ExternalDependencyManager

            from .cli_plugin_manager import CliPluginManager

            _CliPluginManager = CliPluginManager().get_singleton

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True

        def read_plugin_data(self):
            cli_plugin_manager = (
                _CliPluginManager()
            )

            data = (
                (cli_plugin_manager.read_root_data()).get(
                    "display", {}
                ) or {}
            )

            return data

        def read_plugin_data_callbacks(self):
            data = (
                (self.read_plugin_data()).get(
                    "callbacks", {}
                ) or {}
            )

            return data

        def run_callback_on_pre_setup(self):
            callback = (
                (self.read_plugin_data_callbacks()).get(
                    "on_pre_setup", None
                ) or {}
            )

            if not callback:
                return True

            return callback()

        def run_callback_on_post_setup(self):
            callback = (
                (self.read_plugin_data_callbacks()).get(
                    "on_post_setup", None
                ) or {}
            )

            if not callback:
                return True

            return callback()

    _CliDisplayManager = __CliDisplayManager
    _allocate = lambda: None


def CliDisplayManager():
    if _CliDisplayManager is None:
        _allocate()

    return _CliDisplayManager
