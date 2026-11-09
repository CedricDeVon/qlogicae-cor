__all__ = (
    "CliCommandManager",
)

_sys = None
_argparse = None
_ObjectMergeManager = None
_CliPluginManager = None
_CliCommandManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _CliCommandManager

    class __CliCommandManager:
        __slots__ = (
            "_default_setup_options",
            "_parser",
            "_commands",
            "_command_handler",
            "_parsed_arguments",
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
            global _sys
            global _argparse
            global _CliPluginManager
            global _ObjectMergeManager
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )
            _sys = (
                _ExternalDependencyManager().import_module(
                    path="sys",
                )
            )
            _argparse = (
                _ExternalDependencyManager().import_module(
                    path="argparse",
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
            _ObjectMergeManager = (
                _ExternalDependencyManager().import_module(
                    path=".object_merge_manager",
                    package="qlogicae_cor.v3.library",
                    member="ObjectMergeManager",
                    is_member_callable=True,
                )
            )

            self._parser = None
            self._commands = None
            self._command_handler = None
            self._parsed_arguments = None
            self._default_setup_options = {
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
            }

            return True

        def apply_setup_options(self, options):
            if not isinstance(options, (dict)):
                raise ValueError(
                    "'options' must be a dictionary"
                )

            options = (
                _ObjectMergeManager()
                    .get_singleton()
                    .deep_merge(
                        self._default_setup_options,
                        options,
                    )
            )

            return options

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError(
                    "'kwargs' must be a dictionary"
                )

            command_data = (
                kwargs.get(
                    "command",
                    {}
                ) or {}
            )
            if not isinstance(command_data, (dict)):
                raise ValueError(
                    "plugin export property 'command' "
                    "must be a dictinoary"
                )

            command_data = (
                self.apply_setup_options(
                    command_data
                )
            )

            options = (
                command_data.get(
                    "options",
                    {}
                ) or {}
            )
            if not isinstance(options, (dict)):
                raise ValueError(
                    "plugin export property 'command.options' "
                    "must be a dictionary"
                )

            callbacks = (
                command_data.get(
                    "callbacks",
                    {}
                ) or {}
            )
            if not isinstance(callbacks, (dict)):
                raise ValueError(
                    "plugin export property 'command.callbacks' "
                    "must be a dictionary"
                )

            callback_on_pre_setup = (
                callbacks.get(
                    "on_pre_setup",
                    None
                )
            )
            callback_on_post_setup = (
                callbacks.get(
                    "on_post_setup",
                    None
                )
            )

            if (
                callback_on_pre_setup and
                callable(callback_on_pre_setup)
            ):
                callback_on_pre_setup()

            result = True
            result = (
                self.setup_parser(
                    options
                ) and result
            )

            if (
                callback_on_post_setup and
                callable(callback_on_post_setup)
            ):
                callback_on_post_setup()

            return result

        def shutdown(self):
            return True

        def setup_parser(self, options):
            if not isinstance(options, (dict)):
                raise ValueError(
                    "'options' must be a dictionary"
                )

            parser_args = options.get("args") or ()
            parser_kwargs = options.get("kwargs") or {}

            self._parser = _argparse().ArgumentParser(
                *parser_args,
                **parser_kwargs,
            )

            commands = options.get("commands") or ()

            if not commands:
                return True

            subparser_configuration = (
                options.get("subparsers") or {}
            )

            subparser_args = subparser_configuration.get("args") or ()
            subparser_kwargs = subparser_configuration.get("kwargs") or {}

            subparsers = self._parser.add_subparsers(
                *subparser_args,
                **subparser_kwargs,
            )

            for command in commands:
                if not command:
                    continue

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
                    if not argument:
                        continue

                    command_parser.add_argument(
                        *(argument.get("args") or ()),
                        **(argument.get("kwargs") or {}),
                    )

            return True

        def run_parser(self):
            result = True
            result = (
                self.setup_parsed_arguments() and result
            )
            result = (
                self.setup_command_handler() and result
            )
            result = (
                self.run_command_handler() and result
            )
            return (
                result
            )

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

        def run_command_handler(self):
            result = True

            if self._command_handler is not None:
                result = self._command_handler(
                    self._parsed_arguments
                ) and result

            else:
                self._parser.print_help()

            return result

        def read_cli_error_output(self):
            return _sys().stderr

        def read_cli_arguments(self):
            return tuple(_sys().argv[1:])





    _CliCommandManager = __CliCommandManager
    _allocate = lambda: None


def CliCommandManager():
    if _CliCommandManager is None:
        _allocate()

    return _CliCommandManager



# CliCommandManager()
