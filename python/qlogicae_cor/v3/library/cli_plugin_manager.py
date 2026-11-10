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
            self._default_setup_options = {
                "command": {
                    "options": {
                        "args": (),
                        "kwargs": {
                            "prog": "name",
                            "description": "command description",
                            "add_help": True,
                            "allow_abbrev": False,
                        },
                        "commands": [],
                        "subparsers": {
                            "args": (),
                            "kwargs": {
                                "dest": "command",
                                "required": True,
                                "title": "commands",
                                "description": None,
                                "metavar": "",
                            },
                        },
                    },
                    "callbacks": {
                        "on_pre_setup": None,
                        "on_post_setup": None,
                    },
                },
                "database": {
                    "is_enabled": False,
                    "value_cache": {
                        "is_enabled": False,
                        "options": {
                            "values": {},
                            "defaults": {}
                        },
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
                "log": {
                    "is_enabled": False,
                    "file": {
                        "options": {
                            "is_enabled": False,
                            "is_verbose_enabled": True,
                            "log_level": 10,
                            "stack_level": 3,
                            "target_filesystem_paths": [
                                "logs.log"
                            ],
                        },
                        "callbacks": {
                            "on_pre_setup": None,
                            "on_post_setup": None,
                        },
                    },
                    "console": {
                        "options": {
                            "is_enabled": False,
                            "is_verbose_enabled": True,
                            "log_level": 10,
                            "stack_level": 3,
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
            }

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError("'kwargs' must be a dictionary")

            plugin_manager = (
                _PluginManager().get_singleton()
            )

            kwargs = (
                self.write_setup_kwargs(
                    kwargs
                )
            )

            plugin_manager.setup(
                **kwargs
            )
            
            return True

        def shutdown(self):
            return True

        def write_setup_kwargs(self, kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError("'kwargs' must be a dictionary")

            if "initial_export_data" not in kwargs:
                kwargs["initial_export_data"] = (
                    self._default_setup_options
                )

            return kwargs

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
