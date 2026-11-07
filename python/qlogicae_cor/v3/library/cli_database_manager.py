__all__ = (
    "CliDatabaseManager",
)

_ObjectMergeManager = None
_CliPluginManager = None
_CliDatabaseManager = None
_ExternalDependencyManager = None
_ValueCacheStorageManager = None
_PersistentCacheStorageManager = None


def _allocate():
    global _allocate
    global _CliDatabaseManager

    class __CliDatabaseManager:
        __slots__ = (
            "_default_setup_options"
        )

        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @property
        def default_setup_options(self):
            return self._default_setup_options

        @default_setup_options.setter
        def default_setup_options(self, value):
            if not isinstance(value, (dict)):
                raise ValueError(
                    "'value' must be a dictionary"
                )

            self._default_setup_options = value

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _ObjectMergeManager
            global _CliPluginManager
            global _ExternalDependencyManager
            global _ValueCacheStorageManager
            global _PersistentCacheStorageManager

            from .external_dependency_manager import (
                ExternalDependencyManager
            )
            from .object_merge_manager import (
                ObjectMergeManager
            )
            from .cli_plugin_manager import (
                CliPluginManager
            )
            from .value_cache_storage_manager import (
                ValueCacheStorageManager
            )
            from .persistent_cache_storage_manager import (
                PersistentCacheStorageManager
            )

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )
            _CliPluginManager = (
                _ExternalDependencyManager().import_module(
                    path=".cli_plugin_manager",
                    package="qlogicae_cor.v3.library",
                    member="CliPluginManager",
                    is_member_callable=True,
                )
            )
            _ValueCacheStorageManager = (
                _ExternalDependencyManager().import_module(
                    path=".value_cache_storage_manager",
                    package="qlogicae_cor.v3.library",
                    member="ValueCacheStorageManager",
                    is_member_callable=True,
                )
            )
            _PersistentCacheStorageManager = (
                _ExternalDependencyManager().import_module(
                    path=".persistent_cache_storage_manager",
                    package="qlogicae_cor.v3.library",
                    member="PersistentCacheStorageManager",
                    is_member_callable=True,
                )
            )
            _ObjectMergeManager = (
                _ExternalDependencyManager().import_module(
                    path=".object_merge_manager",
                    package="qlogicae_cor.v3.library",
                    member="ObjectMergeManager",
                    is_member_callable=True,
                )
            )

            self._default_setup_options = {
                "is_enabled": False,
                "value_cache": {
                    "is_enabled": False,
                    "options": {
                        "values": {},
                        "defaults": {}
                    }
                    "callbacks": {
                        "on_pre_setup": None,
                        "on_post_setup": None,
                    },
                },
                "persistent_cache": {
                    "is_enabled": False,
                    "options": {
                        "database_path": "persistent_cache.db",
                    },
                    "callbacks": {
                        "on_pre_setup": None,
                        "on_post_setup": None,
                    },
                },
                "callbacks": {
                    "on_pre_setup": None,
                    "on_post_setup": None,
                },
            }

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError(
                    "'kwargs' must be a non-empty dictionary"
                )

            kwargs = (
                self.apply_setup_options(
                    kwargs
                )
            )

            database_is_enabled = (
                kwargs.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(database_is_enabled, (bool)):
                raise ValueError(
                    "'kwargs.is_enabled' must be a boolean"
                )
            if not database_is_enabled:
                return True


            database_callbacks = (
                kwargs.get(
                    "callbacks",
                    {}
                ) or {}
            )
            if not isinstance(database_callbacks, (dict)):
                raise ValueError(
                    f"'kwargs.callbacks' must be a non-empty dictinoary"
                )
            
            database_callback_on_pre_setup = (
                database_callbacks.get(
                    "on_pre_setup",
                    None
                )
            )
            database_callback_on_post_setup = (
                database_callbacks.get(
                    "on_post_setup",
                    None
                )
            )

            if (
                database_callback_on_pre_setup and
                callable(database_callback_on_pre_setup)
            ):
                database_callback_on_pre_setup()

            self.setup_database(
                kwargs,
                "value_cache",
                _ValueCacheStorageManager,
            )
            self.setup_database(
                kwargs,
                "persistent_cache",
                _PersistentCacheStorageManager,
            )

            if (
                database_callback_on_post_setup and
                callable(database_callback_on_post_setup)
            ):
                database_callback_on_post_setup()

            return True

        def shutdown(self):
            return True

        def setup_database(self, kwargs, property_name, class_name):
            if not kwargs or not property_name or not class_name:
                return True

            result = True
            database = (
                kwargs.get(
                    property_name,
                    {}
                ) or {}
            )
            if not isinstance(database, (dict)):
                raise ValueError(
                    f"'kwargs.{property_name}' must be a non-empty dictionary"
                )
            if not database:
                return result

            database_is_enabled = (
                database.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(database_is_enabled, (bool)):
                raise ValueError(
                    f"'kwargs.{property_name}.is_enabled' must be a boolean"
                )

            if database_is_enabled:
                database_options = (
                    database.get(
                        "options",
                        {}
                    ) or {}
                )
                if not isinstance(database_options, (dict)):
                    raise ValueError(
                        f"'kwargs.{property_name}.options' must be a non-empty dictinoary"
                    )
                if not database_options:
                    return result

                database_callbacks = (
                    database.get(
                        "callbacks",
                        {}
                    ) or {}
                )
                if not isinstance(database_callbacks, (dict)):
                    raise ValueError(
                        f"'kwargs.{property_name}.callbacks' must be a non-empty dictinoary"
                    )
                
                database_callback_on_pre_setup = (
                    database_callbacks.get(
                        "on_pre_setup",
                        None
                    )
                )
                database_callback_on_post_setup = (
                    database_callbacks.get(
                        "on_post_setup",
                        None
                    )
                )

                if (
                    database_callback_on_pre_setup and
                    callable(database_callback_on_pre_setup)
                ):
                    database_callback_on_pre_setup()

                result = class_name().get_singleton().setup(
                    **database_options
                )

                if (
                    database_callback_on_post_setup and
                    callable(database_callback_on_post_setup)
                ):
                    database_callback_on_post_setup()

            return result

        def apply_setup_options(self, kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError(
                    "'kwargs' must be a non-empty dictionary"
                )

            kwargs = (
                _ObjectMergeManager()
                    .get_singleton()
                    .deep_merge(
                        self._default_setup_options,
                        kwargs,
                    )
            )

            return kwargs


    _CliDatabaseManager = __CliDatabaseManager
    _allocate = lambda: None


def CliDatabaseManager():
    if _CliDatabaseManager is None:
        _allocate()

    return _CliDatabaseManager

