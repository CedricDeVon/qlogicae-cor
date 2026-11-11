__all__ = (
    "CliAppManager",
)

_CliLogManager = None
_CliAppManager = None
_CliPluginManager = None
_CliCommandManager = None
_CliDatabaseManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _CliAppManager

    class __CliAppManager:
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
            global _CliLogManager
            global _CliPluginManager
            global _CliCommandManager
            global _CliDatabaseManager
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )
            _CliLogManager = (
                _ExternalDependencyManager().import_module(
                    path=".cli_log_manager",
                    package="qlogicae_cor.v3.library",
                    member="CliLogManager",
                    is_member_callable=True,
                )
            )
            _CliPluginManager = (
                _ExternalDependencyManager().import_module(
                    path=".cli_plugin_manager",
                    package="qlogicae_cor.v3.library",
                    member="CliPluginManager",
                    is_member_callable=True,
                )
            )
            _CliDatabaseManager = (
                _ExternalDependencyManager().import_module(
                    path=".cli_database_manager",
                    package="qlogicae_cor.v3.library",
                    member="CliDatabaseManager",
                    is_member_callable=True,
                )
            )
            _CliCommandManager = (
                _ExternalDependencyManager().import_module(
                    path=".cli_command_manager",
                    package="qlogicae_cor.v3.library",
                    member="CliCommandManager",
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

        def run(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            plugin_exports = (
                self.setup_plugin_module_exports(
                    kwargs
                )
            )
            if not plugin_exports:
                return (
                    self.evaluate_output(
                        False
                    )
                )

            result = True
            result = (
                self.setup_logs(
                    plugin_exports
                )
            ) and result
            if not result:
                return (
                    self.evaluate_output(
                        False
                    )
                )

            result = (
                self.setup_databases(
                    plugin_exports
                )
            ) and result
            if not result:
                return (
                    self.evaluate_output(
                        False
                    )
                )

            result = (
                self.setup_commands(
                    plugin_exports
                )
            ) and result
            if not result:
                return (
                    self.evaluate_output(
                        False
                    )
                )

            result = (
                self.run_command_parser(
                    plugin_exports
                )
            ) and result

            return (
                self.evaluate_output(
                    result
                )
            )

        def setup_plugin_module_exports(self, options):
            if not isinstance(options, (dict)) or not options:
                raise ValueError("'options' must be a non-empty dictionary")

            cli_plugin_manager = (
                _CliPluginManager()
                    .get_singleton()
            )

            plugin_options = (
                options.get(
                    "plugin",
                    {}
                ) or {}
            )

            result = (
                cli_plugin_manager
                    .setup(
                        **plugin_options
                    )
            )
            if not result:
                return {}

            plugin_exports = (
                cli_plugin_manager
                    .read_module_exports()
            )

            return (
                plugin_exports
            )

        def setup_logs(self, plugin_exports):
            if not isinstance(plugin_exports, (dict)) or not plugin_exports:
                raise ValueError("'plugin_exports' must be a non-empty dictionary")

            cli_plugin_manager = (
                _CliPluginManager()
                    .get_singleton()
            )

            result = True
            if (
                cli_plugin_manager
                    .is_log_enabled(
                        plugin_exports
                    )
            ):
                result = (
                    _CliLogManager()
                        .get_singleton()
                        .setup(
                            **plugin_exports
                        )
                )

            return result

        def setup_databases(self, plugin_exports):
            if not isinstance(plugin_exports, (dict)) or not plugin_exports:
                raise ValueError("'plugin_exports' must be a non-empty dictionary")

            cli_plugin_manager = (
                _CliPluginManager()
                    .get_singleton()
            )

            result = True
            if (
                cli_plugin_manager
                    .is_database_enabled(
                        plugin_exports
                    )
            ):
                result = (
                    _CliDatabaseManager()
                        .get_singleton()
                        .setup(
                            **plugin_exports
                        )
                )

            return result

        def setup_commands(self, plugin_exports):
            if not isinstance(plugin_exports, (dict)) or not plugin_exports:
                raise ValueError("'plugin_exports' must be a non-empty dictionary")

            cli_command_manager = (
                _CliCommandManager()
                    .get_singleton()
            )

            result = (
                cli_command_manager
                    .setup(
                        **plugin_exports
                    )
            )

            return result

        def run_command_parser(self, plugin_exports):
            if not isinstance(plugin_exports, (dict)) or not plugin_exports:
                raise ValueError("'plugin_exports' must be a non-empty dictionary")

            cli_command_manager = (
                _CliCommandManager()
                    .get_singleton()
            )

            result = (
                cli_command_manager
                    .run_parser(
                        plugin_exports
                    )

            )

            return result


        def evaluate_output(self, value):
            return 0 if value else 1


    _CliAppManager = __CliAppManager
    _allocate = lambda: None


def CliAppManager():
    if _CliAppManager is None:
        _allocate()

    return _CliAppManager

