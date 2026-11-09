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

            from .external_dependency_manager import ExternalDependencyManager

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

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)):
                raise ValueError(
                    "'kwargs' must be a dictionary"
                )

            log_data = (
                kwargs.get(
                    "log",
                    {}
                ) or {}
            )
            if not isinstance(log_data, (dict)):
                raise ValueError(
                    "plugin export property 'log' "
                    "must be a dictinoary"
                )

            log_data = (
                self.apply_setup_options(
                    log_data
                )
            )
            log_is_enabled = (
                log_data.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(log_is_enabled, (bool)):
                raise ValueError(
                    "plugin export property 'log.is_enabled' "
                    "must be a boolean"
                )
            if not log_is_enabled:
                return True

            log_callbacks = (
                log_data.get(
                    "callbacks",
                    {}
                ) or {}
            )
            if not isinstance(log_callbacks, (dict)):
                raise ValueError(
                    "plugin export property 'log.callbacks' "
                    "must be a dictinoary"
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
                log_data,
                "file",
                _FileLogManager,
            )
            self.setup_logger(
                log_data,
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

        def setup_logger(self, options, property_name, class_name):
            if not isinstance(options, (dict)):
                raise ValueError(
                    "'options' must be a dictionary"
                )
            if not isinstance(property_name, (str)):
                raise ValueError(
                    "'property_name' must be a string"
                )
            if not class_name:
                raise ValueError(
                    "'class_name' must be defined"
                )

            result = True
            log_data = (
                options.get(
                    property_name,
                    {}
                ) or {}
            )
            if not isinstance(log_data, (dict)):
                raise ValueError(
                    "plugin export property "
                    "'log.{property_name}' "
                    "must be a dictionary"
                )

            log_data_options = (
                log_data.get(
                    "options",
                    {}
                ) or {}
            )
            if not isinstance(log_data_options, (dict)):
                raise ValueError(
                    "plugin export property "
                    "'log.{property_name}.options' "
                    "must be a dictinoary"
                )

            log_data_is_enabled = (
                log_data_options.get(
                    "is_enabled",
                    False
                )
            )
            if not isinstance(log_data_is_enabled, (bool)):
                raise ValueError(
                    "plugin export property "
                    "'log.{property_name}.options.is_enabled' "
                    "must be a boolean"
                )

            if log_data_is_enabled:
                log_data_callbacks = (
                    log_data.get(
                        "callbacks",
                        {}
                    ) or {}
                )
                if not isinstance(log_data_callbacks, (dict)):
                    raise ValueError(
                        "plugin export property "
                        "'log.{property_name}.callbacks' "
                        "must be a dictinoary"
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
                    options=_LogOptions()(
                        **log_data_options
                    )
                )

                if (
                    log_data_callback_on_post_setup and
                    callable(log_data_callback_on_post_setup)
                ):
                    log_data_callback_on_post_setup()

            return result

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


    _CliLogManager = __CliLogManager
    _allocate = lambda: None


def CliLogManager():
    if _CliLogManager is None:
        _allocate()

    return _CliLogManager



# CliLogManager()
