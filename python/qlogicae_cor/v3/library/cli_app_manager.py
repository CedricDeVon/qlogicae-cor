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

            return result

        def run(self):
            try:
                result = True

                result = (
                    self.setup_parsed_arguments() and result
                )
                result = (
                    self.setup_command_handler() and result
                )
                result = (
                    self.parse_arguments() and result
                )

            except (OSError, ValueError, RuntimeError) as error:
                print(f"\033[91m{error}\033[0m")
                result = False

            return (
                self.evaluate_cli_output(
                    result
                )
            )

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
            plugin_manager = (
                PluginManager().get_singleton()
            )
            if not plugin_manager:
                return False

            module_exports = (
                plugin_manager.module_exports
            )
            if not module_exports:
                return False

            self._parser = _argparse.ArgumentParser(
                *module_exports.get("args", ()),
                **module_exports.get("kwargs", {}),
            )

            commands = module_exports.get("commands", ())

            if not commands:
                return False

            subparser_configuration = module_exports.get(
                "subparsers",
                {},
            )

            subparsers = self._parser.add_subparsers(
                *subparser_configuration.get("args", ()),
                **subparser_configuration.get("kwargs", {}),
            )

            for command in commands:
                command_parser = subparsers.add_parser(
                    command["name"],
                    *command.get("args", ()),
                    **command.get("kwargs", {}),
                )

                command_handler = command.get("command_handler")

                if command_handler is not None:
                    command_parser.set_defaults(
                        command_handler=command_handler,
                    )

                for argument in command.get("arguments", ()):
                    command_parser.add_argument(
                        *argument.get("args", ()),
                        **argument.get("kwargs", {}),
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
