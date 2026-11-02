__all__ = (
    "CliDatabaseManager",
)

_PluginManager = None
_CliPluginManager = None
_ValueCacheManager = None
_CliDatabaseManager = None
_PythonRuntimeUtilityManager = None
_PersistentCacheStorageManager = None


def _allocate_module():
    global _allocate_module
    global _CliDatabaseManager

    class __CliDatabaseManager:
        __slots__ = ()

        _singleton = None

        def __init__(self):
            self.construct()

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _PluginManager
            global _CliPluginManager
            global _ValueCacheManager
            global _PythonRuntimeUtilityManager
            global _PersistentCacheStorageManager

            from .persistent_cache_storage_manager import PersistentCacheStorageManager
            from .plugin_manager import PluginManager
            from .python_runtime_utility_manager import PythonRuntimeUtilityManager
            from .value_cache_manager import ValueCacheManager

            _PluginManager = PluginManager().get_singleton
            _ValueCacheManager = ValueCacheManager().get_singleton
            _PythonRuntimeUtilityManager = (
                PythonRuntimeUtilityManager().get_singleton
            )
            _PersistentCacheStorageManager = (
                PersistentCacheStorageManager().get_singleton
            )

            if (
                _PythonRuntimeUtilityManager()
                    .is_allocated_during_object_construction
            ):
                _PluginManager()

            return True

        def setup(self):
            if not self.read_plugin_data_is_enabled():
                return True

            self.run_callback_on_pre_setup()

            if self.read_plugin_data_value_cache_is_enabled():
                value_cache_manager = (
                    _ValueCacheManager()
                )
                value_cache_manager.setup(
                    data=self.read_plugin_data_value_cache_data()
                )

            if self.read_plugin_data_persistent_cache_is_enabled():
                persistent_cache_manager = (
                    _PersistentCacheStorageManager()
                )
                persistent_cache_manager.setup(
                    **self.read_plugin_data_persistent_cache_options()
                )

            self.run_callback_on_post_setup()

            return True

        def shutdown(self):
            return True

        def read_plugin_data(self):
            cli_plugin_manager = (
                _CliPluginManager()
            )

            data = (
                (cli_plugin_manager.read_root()).get(
                    "database", {}
                ) or {}
            )

            return data

        def read_plugin_data_is_enabled(self):
            data = (
                (self.read_plugin_data()).get(
                    "is_enabled", False
                )
            )

            return data

        def read_plugin_data_value_cache(self):
            data = (
                (self.read_plugin_data()).get(
                    "value_cache", {}
                ) or {}
            )

            return data

        def read_plugin_data_persisent_cache(self):
            data = (
                (self.read_plugin_data()).get(
                    "persisent_cache", {}
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

        def read_plugin_data_value_cache_is_enabled(self):
            data = (
                (self.read_plugin_data_value_cache()).get(
                    "is_enabled", False
                )
            )

            return data

        def read_plugin_data_value_cache_data(self):
            data = (
                (self.read_plugin_data_value_cache()).get(
                    "data", {}
                ) or {}
            )

            return data

        def read_plugin_data_persistent_cache_is_enabled(self):
            data = (
                (self.read_plugin_data_persistent_cache()).get(
                    "is_enabled", False
                )
            )

            return data

        def read_plugin_data_persistent_cache_data(self):
            data = (
                (self.read_plugin_data_persistent_cache()).get(
                    "data", {}
                ) or {}
            )

            return data

        def read_plugin_data_persistent_cache_options(self):
            data = (
                (self.read_plugin_data_persistent_cache()).get(
                    "options", {}
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


    _CliDatabaseManager = __CliDatabaseManager
    _allocate_module = lambda: None


def CliDatabaseManager():
    if _CliDatabaseManager is None:
        _allocate_module()

    return _CliDatabaseManager
