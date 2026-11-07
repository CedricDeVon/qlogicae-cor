__all__ = (
    "CliLogManager",
)

_ObjectMergeManager = None
_LogOptions = None
_CliLogManager = None
_FileLogManager = None
_CliPluginManager = None
_ConsoleLogManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _CliLogManager

    class __CliLogManager:
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
            global _LogOptions
            global _FileLogManager
            global _ConsoleLogManager
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
            from .log_options import (
                LogOptions
            )
            from .file_log_manager import (
                FileLogManager
            )
            from .console_log_manager import (
                ConsoleLogManager
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
            _LogOptions = (
                _ExternalDependencyManager().import_module(
                    path=".log_options",
                    package="qlogicae_cor.v3.library",
                    member="LogOptions",
                    is_member_callable=True,
                )
            )
            _FileLogManager = (
                _ExternalDependencyManager().import_module(
                    path=".file_log_manager",
                    package="qlogicae_cor.v3.library",
                    member="FileLogManager",
                    is_member_callable=True,
                )
            )
            _ConsoleLogManager = (
                _ExternalDependencyManager().import_module(
                    path=".console_log_manager",
                    package="qlogicae_cor.v3.library",
                    member="ConsoleLogManager",
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
                "file": {
                    "options": {
                        "is_enabled": False,
                        "is_verbose_enabled": True,
                        "log_level": 10,
                        "stack_level": 3,
                        "targets": [
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

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError(
                    "'kwargs' must be a non-empty dictionary"
                )

            kwargs = (
                self.apply_setup_options(
                    kwargs
                )
            )

            log_is_enabled = (
                kwargs.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(log_is_enabled, (bool)):
                raise ValueError(
                    "'kwargs.is_enabled' must be a boolean"
                )
            if not log_is_enabled:
                return True

            log_callbacks = (
                kwargs.get(
                    "callbacks",
                    {}
                ) or {}
            )
            if not isinstance(log_callbacks, (dict)):
                raise ValueError(
                    f"'kwargs.callbacks' must be a non-empty dictinoary"
                )
            
            log_callback_on_pre_setup = (
                log_callbacks.get(
                    "on_pre_setup",
                    None
                )
            )
            log_callback_on_post_setup = (
                log_callbacks.get(
                    "on_post_setup",
                    None
                )
            )

            if (
                log_callback_on_pre_setup and
                callable(log_callback_on_pre_setup)
            ):
                log_callback_on_pre_setup()

            self.setup_logger(
                kwargs,
                "file",
                _FileLogManager,
            )
            self.setup_logger(
                kwargs,
                "console",
                _ConsoleLogManager,
            )

            if (
                log_callback_on_post_setup and
                callable(log_callback_on_post_setup)
            ):
                log_callback_on_post_setup()


            return True

        def shutdown(self):
            return True

        def setup_logger(self, kwargs, property_name, class_name):
            if not kwargs or not property_name or not class_name:
                return True

            result = True
            log_data = (
                kwargs.get(
                    property_name,
                    {}
                ) or {}
            )
            if not isinstance(log_data, (dict)):
                raise ValueError(
                    f"'kwargs.{property_name}' must be a non-empty dictionary"
                )
            if not log_data:
                return result

            log_data_is_enabled = (
                log_data.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(log_data_is_enabled, (bool)):
                raise ValueError(
                    f"'kwargs.{property_name}.is_enabled' must be a boolean"
                )

            if log_data_is_enabled:
                log_data_options = (
                    log_data.get(
                        "options",
                        {}
                    ) or {}
                )
                if not isinstance(log_data_options, (dict)):
                    raise ValueError(
                        f"'kwargs.{property_name}.options' must be a non-empty dictinoary"
                    )
                if not log_data_options:
                    return result

                log_data_callbacks = (
                    log_data.get(
                        "callbacks",
                        {}
                    ) or {}
                )
                if not isinstance(log_data_callbacks, (dict)):
                    raise ValueError(
                        f"'kwargs.{property_name}.callbacks' must be a non-empty dictinoary"
                    )
                
                log_data_callback_on_pre_setup = (
                    log_data_callbacks.get(
                        "on_pre_setup",
                        None
                    )
                )
                log_data_callback_on_post_setup = (
                    log_data_callbacks.get(
                        "on_post_setup",
                        None
                    )
                )

                if (
                    log_data_callback_on_pre_setup and
                    callable(log_data_callback_on_pre_setup)
                ):
                    log_data_callback_on_pre_setup()

                result = class_name().get_singleton().setup(
                    options=_LogOptions(
                        **log_data_options
                    )
                )

                if (
                    log_data_callback_on_post_setup and
                    callable(log_data_callback_on_post_setup)
                ):
                    log_data_callback_on_post_setup()

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


    _CliLogManager = __CliLogManager
    _allocate = lambda: None


def CliLogManager():
    if _CliLogManager is None:
        _allocate()

    return _CliLogManager


# __all__ = (
#     "CliLogManager",
# )

# _LogOptions = None
# _FileLogManager = None
# _ConsoleLogManager = None
# _CliLogManager = None
# _CliPluginManager = None
# _ExternalDependencyManager = None


# def _allocate():
#     global _allocate
#     global _CliLogManager

#     class __CliLogManager:
#         __slots__ = ()

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
#             global _LogOptions
#             global _CliPluginManager
#             global _ExternalDependencyManager

#             from .cli_plugin_manager import CliPluginManager
#             from .log_options import LogOptions

#             _LogOptions = LogOptions()
#             _CliPluginManager = (
#                 CliPluginManager().get_singleton
#             )

#             return True

#         def setup(self, **kwargs):
#             if not kwargs:
#                 return False

#             if not self.read_plugin_data_is_enabled():
#                 return True

#             self.run_callback_on_pre_setup()

#             if self.read_plugin_data_file_options_is_enabled():
#                 global _FileLogManager

#                 from .file_log_manager import FileLogManager

#                 _FileLogManager = (
#                     FileLogManager().get_singleton
#                 )

#                 file_log_manager = (
#                     _FileLogManager()
#                 )
#                 file_log_manager.setup(
#                     options=_LogOptions(
#                         **self.read_plugin_data_file_options(),
#                     ),
#                     target_filesystem_paths=(
#                         self.read_plugin_data_file_targets()
#                     )
#                 )

#             if self.read_plugin_data_console_options_is_enabled():
#                 global _ConsoleLogManager

#                 from .console_log_manager import ConsoleLogManager

#                 _ConsoleLogManager = (
#                     ConsoleLogManager().get_singleton
#                 )

#                 console_log_manager = (
#                     _ConsoleLogManager()
#                 )
#                 console_log_manager.setup(
#                     options=_LogOptions(
#                         **self.read_plugin_data_console_options(),
#                     ),
#                 )

#             self.run_callback_on_post_setup()

#             return True

#         def shutdown(self):
#             console_log_manager = (
#                 _ConsoleLogManager()
#             )
#             file_log_manager = (
#                 _FileLogManager()
#             )

#             console_log_manager.shutdown()
#             file_log_manager.shutdown()

#             return True

#         def read_plugin_data(self):
#             cli_plugin_manager = (
#                 _CliPluginManager()
#             )

#             data = (
#                 (cli_plugin_manager.read_root_data()).get(
#                     "log", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_is_enabled(self):
#             data = (
#                 self.read_plugin_data().get(
#                     "is_enabled", False
#                 )
#             )

#             return data

#         def read_plugin_data_file(self):
#             data = (
#                 (self.read_plugin_data()).get(
#                     "file", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_file_options(self):
#             data = (
#                 (self.read_plugin_data_file()).get(
#                     "options", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_file_options_is_enabled(self):
#             data = (
#                 (self.read_plugin_data_file_options()).get(
#                     "is_enabled", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_file_targets(self):
#             data = (
#                 (self.read_plugin_data_file()).get(
#                     "targets", tuple()
#                 ) or tuple()
#             )

#             return data

#         def read_plugin_data_console(self):
#             data = (
#                 (self.read_plugin_data()).get(
#                     "console", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_console_options(self):
#             data = (
#                 (self.read_plugin_data_console()).get(
#                     "options", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_console_options_is_enabled(self):
#             data = (
#                 (self.read_plugin_data_console_options()).get(
#                     "is_enabled", {}
#                 ) or {}
#             )

#             return data

#         def read_plugin_data_callbacks(self):
#             data = (
#                 (self.read_plugin_data()).get(
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


#     _CliLogManager = __CliLogManager
#     _allocate = lambda: None


# def CliLogManager():
#     if _CliLogManager is None:
#         _allocate()

#     return _CliLogManager
