__all__ = (
    "CliAppManager",
)

_sys = None
_argparse = None
_CliAppManager = None
_PluginManager = None
_PythonRuntimeUtilityManager = None


def _allocate_module():
    global _allocate_module

    global _sys
    global _argparse
    global _CliAppManager
    global _PluginManager
    global _PythonRuntimeUtilityManager

    import argparse
    import sys

    from .plugin_manager import PluginManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager

    _sys = sys
    _argparse = argparse
    _PluginManager = PluginManager().get_singleton
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()

    class __CliAppManager:
        __slots__ = (
            "_options",
            "_parser",
            "_commands",
            "_command_handler",
            "_parsed_arguments",
        )

        _singleton = None

        def __init__(self):
            if (
                _PythonRuntimeUtilityManager
                    .is_allocated_during_object_construction
            ):
                _PluginManager()

            self._options = None
            self._parser = None
            self._commands = None
            self._command_handler = None
            self._parsed_arguments = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def setup(self, **kwargs):
            if not kwargs:
                return False

            options = (
                kwargs.get(
                    "options",
                    {}
                ) or {}
            )
            if not options:
                return False

            self._options = (
                options
            )

            result = True

            result = (
                self.setup_exports() and result
            )
            result = (
                self.setup_parser() and result
            )
            result = (
                self.setup_parsed_arguments() and result
            )
            result = (
                self.setup_command_handler() and result
            )

            return result

        def run(self):
            try:
                result = True

                result = (
                    self.parse_arguments() and result
                )

            except (OSError, ValueError, RuntimeError) as error:
                self.print_error(error)
                result = False

            return (
                self.evaluate_cli_output(
                    result
                )
            )

        def print_error(self, message):
            print(f"\033[91m{message}\033[0m")

            return True

        def evaluate_cli_output(self, value):
            return 0 if value else 1

        def read_cli_error_output(self):
            return _sys.stderr

        def read_cli_arguments(self):
            return tuple(_sys.argv[1:])

        def setup_exports(self):
            plugin_manager = (
                PluginManager().get_singleton()
            )

            options_extraction = (
                self._options.get(
                    "extraction",
                    {}
                ) or {}
            )

            plugin_manager.setup(
                options=options_extraction
            )

            return True

        def setup_parser(self):
            plugin_manager = PluginManager().get_singleton()

            if plugin_manager is None:
                return False

            module_exports = plugin_manager.module_exports or {}

            plugin_module_exports = module_exports.get("cli") or {}

            if not isinstance(plugin_module_exports, dict):
                return False

            parser_args = plugin_module_exports.get("args") or ()
            parser_kwargs = plugin_module_exports.get("kwargs") or {}

            self._parser = _argparse.ArgumentParser(
                *parser_args,
                **parser_kwargs,
            )

            commands = plugin_module_exports.get("commands") or ()

            if not commands:
                return True

            subparser_configuration = (
                plugin_module_exports.get("subparsers") or {}
            )

            subparser_args = subparser_configuration.get("args") or ()
            subparser_kwargs = subparser_configuration.get("kwargs") or {}

            subparsers = self._parser.add_subparsers(
                *subparser_args,
                **subparser_kwargs,
            )

            for command in commands:
                command_parser = subparsers.add_parser(
                    command["name"],
                    *(command.get("args") or ()),
                    **(command.get("kwargs") or {}),
                )

                command_handler = command.get("command_handler")

                if command_handler is not None:
                    command_parser.set_defaults(
                        command_handler=command_handler,
                    )

                arguments = command.get("arguments") or ()

                for argument in arguments:
                    command_parser.add_argument(
                        *(argument.get("args") or ()),
                        **(argument.get("kwargs") or {}),
                    )

            return True

        def setup_parsed_arguments(self):
            arguments = self._parser.parse_args()

            self._parsed_arguments = (
                arguments
            )

            return True

        def setup_command_handler(self):
            self._command_handler = getattr(
                self._parsed_arguments,
                "command_handler",
                None,
            )

            return True

        def parse_arguments(self):
            result = True

            if self._command_handler is not None:
                result = self._command_handler(
                    self._parsed_arguments
                ) and result

            else:
                self._parser.print_help()

            return result

    _CliAppManager = __CliAppManager
    _allocate_module = lambda: None


def CliAppManager():
    if _CliAppManager is None:
        _allocate_module()

    return _CliAppManager


# CliAppManager().get_singleton().setup(
#     options={
#         "extraction": {
#             "target_filesystem_paths": (
#                 "./qlogicae_cor/v3/library/plugin"
#             ),
#         }
#     }
# )
# CliAppManager().get_singleton().run()
