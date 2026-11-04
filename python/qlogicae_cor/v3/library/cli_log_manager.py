__all__ = (
    "CliLogManager",
)

_LogOptions = None
_CliLogManager = None
_FileLogManager = None
_ConsoleLogManager = None
_CliPluginManager = None
_PythonRuntimeUtilityManager = None


def _allocate():
    global _allocate
    global _CliLogManager

    class __CliLogManager:
        __slots__ = ()

        _singleton = None

        def __init__(self):
            self.construct()

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _LogOptions
            global _CliPluginManager
            global _PythonRuntimeUtilityManager

            from .cli_plugin_manager import CliPluginManager
            from .log_options import LogOptions
            from .python_runtime_utility_manager import PythonRuntimeUtilityManager

            _LogOptions = LogOptions()
            _CliPluginManager = (
                CliPluginManager().get_singleton
            )
            _PythonRuntimeUtilityManager = (
                PythonRuntimeUtilityManager().get_singleton
            )

            if (
                _PythonRuntimeUtilityManager()
                    .is_allocated_during_object_construction
            ):
                _CliPluginManager()

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            if not self.read_plugin_data_is_enabled():
                return True

            self.run_callback_on_pre_setup()

            if self.read_plugin_data_file_options_is_enabled():
                global _FileLogManager

                from .file_log_manager import FileLogManager

                _FileLogManager = (
                    FileLogManager().get_singleton
                )

                file_log_manager = (
                    _FileLogManager()
                )
                file_log_manager.setup(
                    options=_LogOptions(
                        **self.read_plugin_data_file_options(),
                    ),
                    target_filesystem_paths=(
                        self.read_plugin_data_file_targets()
                    )
                )

            if self.read_plugin_data_console_options_is_enabled():
                global _ConsoleLogManager

                from .console_log_manager import ConsoleLogManager

                _ConsoleLogManager = (
                    ConsoleLogManager().get_singleton
                )

                console_log_manager = (
                    _ConsoleLogManager()
                )
                console_log_manager.setup(
                    options=_LogOptions(
                        **self.read_plugin_data_console_options(),
                    ),
                )

            self.run_callback_on_post_setup()

            return True

        def shutdown(self):
            console_log_manager = (
                _ConsoleLogManager()
            )
            file_log_manager = (
                _FileLogManager()
            )

            console_log_manager.shutdown()
            file_log_manager.shutdown()

            return True

        def read_plugin_data(self):
            cli_plugin_manager = (
                _CliPluginManager()
            )

            data = (
                (cli_plugin_manager.read_root_data()).get(
                    "log", {}
                ) or {}
            )

            return data

        def read_plugin_data_is_enabled(self):
            data = (
                self.read_plugin_data().get(
                    "is_enabled", False
                )
            )

            return data

        def read_plugin_data_file(self):
            data = (
                (self.read_plugin_data()).get(
                    "file", {}
                ) or {}
            )

            return data

        def read_plugin_data_file_options(self):
            data = (
                (self.read_plugin_data_file()).get(
                    "options", {}
                ) or {}
            )

            return data

        def read_plugin_data_file_options_is_enabled(self):
            data = (
                (self.read_plugin_data_file_options()).get(
                    "is_enabled", {}
                ) or {}
            )

            return data

        def read_plugin_data_file_targets(self):
            data = (
                (self.read_plugin_data_file()).get(
                    "targets", tuple()
                ) or tuple()
            )

            return data

        def read_plugin_data_console(self):
            data = (
                (self.read_plugin_data()).get(
                    "console", {}
                ) or {}
            )

            return data

        def read_plugin_data_console_options(self):
            data = (
                (self.read_plugin_data_console()).get(
                    "options", {}
                ) or {}
            )

            return data

        def read_plugin_data_console_options_is_enabled(self):
            data = (
                (self.read_plugin_data_console_options()).get(
                    "is_enabled", {}
                ) or {}
            )

            return data

        def read_plugin_data_callbacks(self):
            data = (
                (self.read_plugin_data()).get(
                    "callbacks", {}
                ) or {}
            )

            return data

        def run_callback_on_pre_setup(self):
            callback = (
                (self.read_plugin_data_callbacks()).get(
                    "on_pre_setup", None
                ) or {}
            )

            if not callback:
                return True

            return callback()

        def run_callback_on_post_setup(self):
            callback = (
                (self.read_plugin_data_callbacks()).get(
                    "on_post_setup", None
                ) or {}
            )

            if not callback:
                return True

            return callback()


    _CliLogManager = __CliLogManager
    _allocate = lambda: None


def CliLogManager():
    if _CliLogManager is None:
        _allocate()

    return _CliLogManager
