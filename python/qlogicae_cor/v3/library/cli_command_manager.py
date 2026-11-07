__all__ = (
    "CliCommandManager",
)

_ObjectMergeManager = None
_CliPluginManager = None
_CliCommandManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _CliCommandManager

    class __CliCommandManager:
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
            global _CliPluginManager
            global _ObjectMergeManager
            global _ExternalDependencyManager

            from .external_dependency_manager import (
                ExternalDependencyManager
            )
            from .object_merge_manager import (
                ObjectMergeManager
            )
            from .cli_plugin_manager import (
                CliPluginManager
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
            _ObjectMergeManager = (
                _ExternalDependencyManager().import_module(
                    path=".object_merge_manager",
                    package="qlogicae_cor.v3.library",
                    member="ObjectMergeManager",
                    is_member_callable=True,
                )
            )

            self._default_setup_options = {}

            return True

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

            options = (
                kwargs.get(
                    "options",
                    {}
                ) or {}
            )
            if not isinstance(options, (dict)):
                raise ValueError(
                    "'kwargs.options' must be a non-empty dictionary"
                )

            return True

        def shutdown(self):
            return True


    _CliCommandManager = __CliCommandManager
    _allocate = lambda: None


def CliCommandManager():
    if _CliCommandManager is None:
        _allocate()

    return _CliCommandManager



# __all__ = (
#     "CliCommandManager",
# )

# _sys = None
# _argparse = None
# _CliPluginManager = None
# _CliCommandManager = None
# _ExternalDependencyManager = None


# def _allocate():
#     global _allocate
#     global _CliCommandManager

#     class __CliCommandManager:
#         __slots__ = (
#             "_parser",
#             "_commands",
#             "_command_handler",
#             "_parsed_arguments",
#         )

#         _singleton = None

#         def __init__(self):
#             self.construct()

#         def __enter__(self):
#             return self

#         def __exit__(self, exc_type, exc_value, traceback):
#             self.shutdown()

#         @classmethod
#         def get_singleton(cls):
#             if cls._singleton is None:
#                 cls._singleton = cls()

#             return cls._singleton

#         def construct(self):
#             global _sys
#             global _argparse
#             global _CliPluginManager
#             global _ExternalDependencyManager

#             import argparse
#             import sys

#             from .cli_plugin_manager import CliPluginManager

#             _sys = sys
#             _argparse = argparse
#             _CliPluginManager = CliPluginManager().get_singleton

#             self._parser = None
#             self._commands = None
#             self._command_handler = None
#             self._parsed_arguments = None

#             return True

#         def setup(self, **kwargs):
#             if not kwargs:
#                 pass

#             result = True
#             result = (
#                 self.run_callback_on_pre_setup() and result
#             )
#             result = (
#                 self.setup_parser() and result
#             )
#             result = (
#                 self.run_callback_on_post_setup() and result
#             )

#             return result

#         def shutdown(self):
#             return True

#         def run(self):
#             result = True
#             result = (
#                 self.run_callback_on_pre_run() and result
#             )
#             result = (
#                 self.setup_parsed_arguments() and result
#             )
#             result = (
#                 self.setup_command_handler() and result
#             )
#             result = (
#                 self.run_command_handler() and result
#             )
#             result = (
#                 self.run_callback_on_post_run() and result
#             )
#             return (
#                 result
#             )

#         def setup_parsed_arguments(self):
#             arguments = self._parser.parse_args()

#             self._parsed_arguments = (
#                 arguments
#             )

#             return True

#         def setup_command_handler(self):
#             self._command_handler = getattr(
#                 self._parsed_arguments,
#                 "command_handler",
#                 None,
#             )

#             return True

#         def run_command_handler(self):
#             result = True

#             if self._command_handler is not None:
#                 result = self._command_handler(
#                     self._parsed_arguments
#                 ) and result

#             else:
#                 self._parser.print_help()

#             return result

#         def read_cli_error_output(self):
#             return _sys.stderr

#         def read_cli_arguments(self):
#             return tuple(_sys.argv[1:])

#         def setup_parser(self):
#             data_layout = (
#                 self.read_plugin_data_layout()
#             )

#             if not data_layout:
#                 return False

#             if not isinstance(data_layout, dict):
#                 return False

#             parser_args = data_layout.get("args") or ()
#             parser_kwargs = data_layout.get("kwargs") or {}

#             self._parser = _argparse.ArgumentParser(
#                 *parser_args,
#                 **parser_kwargs,
#             )

#             commands = data_layout.get("commands") or ()

#             if not commands:
#                 return True

#             subparser_configuration = (
#                 data_layout.get("subparsers") or {}
#             )

#             subparser_args = subparser_configuration.get("args") or ()
#             subparser_kwargs = subparser_configuration.get("kwargs") or {}

#             subparsers = self._parser.add_subparsers(
#                 *subparser_args,
#                 **subparser_kwargs,
#             )

#             for command in commands:
#                 if not command:
#                     continue

#                 command_parser = subparsers.add_parser(
#                     command["name"],
#                     *(command.get("args") or ()),
#                     **(command.get("kwargs") or {}),
#                 )

#                 command_handler = command.get("command_handler")

#                 if command_handler is not None:
#                     command_parser.set_defaults(
#                         command_handler=command_handler,
#                     )

#                 arguments = command.get("arguments") or ()

#                 for argument in arguments:
#                     if not argument:
#                         continue

#                     command_parser.add_argument(
#                         *(argument.get("args") or ()),
#                         **(argument.get("kwargs") or {}),
#                     )

#             return True

#         def read_plugin_data_layout(self):
#             cli_plugin_manager = (
#                 _CliPluginManager()
#             )

#             data = (
#                 (cli_plugin_manager.read_root_data()).get(
#                     "layout", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_callbacks(self):
#             cli_plugin_manager = (
#                 _CliPluginManager()
#             )

#             data = (
#                 (cli_plugin_manager.read_root_data()).get(
#                     "callbacks", {}
#                 ) or {}
#             )

#             return data

#         def run_callback_on_pre_setup(self):
#             callback = (
#                 (self.read_plugin_data_callbacks()).get(
#                     "on_pre_setup", None
#                 ) or {}
#             )

#             if not callback:
#                 return True

#             return callback()

#         def run_callback_on_post_setup(self):
#             callback = (
#                 (self.read_plugin_data_callbacks()).get(
#                     "on_post_setup", None
#                 ) or {}
#             )

#             if not callback:
#                 return True

#             return callback()

#         def run_callback_on_pre_run(self):
#             callback = (
#                 (self.read_plugin_data_callbacks()).get(
#                     "on_pre_run", None
#                 ) or {}
#             )

#             if not callback:
#                 return True

#             return callback()

#         def run_callback_on_post_run(self):
#             callback = (
#                 (self.read_plugin_data_callbacks()).get(
#                     "on_post_run", None
#                 ) or {}
#             )

#             if not callback:
#                 return True

#             return callback()


#     _CliCommandManager = __CliCommandManager
#     _allocate = lambda: None


# def CliCommandManager():
#     if _CliCommandManager is None:
#         _allocate()

#     return _CliCommandManager
