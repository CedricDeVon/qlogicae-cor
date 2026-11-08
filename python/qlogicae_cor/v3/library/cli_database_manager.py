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
                "database": {
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
                            "create_missing": True,
                            "lifespan_in_seconds": 0.0,
                            "file_mode": 0o600,
                            "key_encoding": "utf-8",
                            "auto_remove_expired": True,
                            "auto_remove_invalid": True,
                            "sync_on_write": False,
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
                },
            }

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError(
                    "'kwargs' must be a dictionary"
                )

            kwargs = (
                self.apply_setup_options(
                    kwargs
                )
            )

            database_data = (
                kwargs.get(
                    "database",
                    {}
                ) or {}
            )
            if not isinstance(database_data, (dict)):
                raise ValueError(
                    f"plugin export property 'database' "
                    "must be a dictinoary"
                )

            database_is_enabled = (
                database_data.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(database_is_enabled, (bool)):
                raise ValueError(
                    "plugin export property 'database.is_enabled' "
                    "must be a boolean"
                )
            if not database_is_enabled:
                return True


            database_callbacks = (
                database_data.get(
                    "callbacks",
                    {}
                ) or {}
            )
            if not isinstance(database_callbacks, (dict)):
                raise ValueError(
                    f"plugin export property 'database.callbacks' "
                    "must be a dictinoary"
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
            if not isinstance(kwargs, (dict)):
                raise ValueError(
                    f"'kwargs' must be a dictionary"
                )
            if not isinstance(property_name, (dict)):
                raise ValueError(
                    f"'property_name' must be a string"
                )
            if not class_name:
                raise ValueError(
                    f"'class_name' must be defined"
                )

            result = True
            database_data = (
                kwargs.get(
                    property_name,
                    {}
                ) or {}
            )
            if not isinstance(database_data, (dict)):
                raise ValueError(
                    f"plugin export property "
                    "'database.{property_name}' "
                    "must be a dictionary"
                )

            database_is_enabled = (
                database_data.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(database_is_enabled, (bool)):
                raise ValueError(
                    f"plugin export property "
                    "'database.{property_name}.is_enabled' "
                    "must be a boolean"
                )

            if database_is_enabled:
                database_options = (
                    database_data.get(
                        "options",
                        {}
                    ) or {}
                )
                if not isinstance(database_options, (dict)):
                    raise ValueError(
                        f"plugin export property "
                        "'database.{property_name}.options' "
                        "must be a dictinoary"
                    )

                database_callbacks = (
                    database_data.get(
                        "callbacks",
                        {}
                    ) or {}
                )
                if not isinstance(database_callbacks, (dict)):
                    raise ValueError(
                        f"plugin export property "
                        "'database.{property_name}.callbacks' "
                        "must be a dictinoary"
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

