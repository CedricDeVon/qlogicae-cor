__all__ = (
    "LogManager",
)

_logging = None
_PythonRuntimeUtilityManager = None
_ConsoleLogManager = None
_FileLogManager = None
_LogOptionsManager = None
_LogManager = None


def _allocate_module():
    global _allocate_module
    global _logging
    global _PythonRuntimeUtilityManager
    global _ConsoleLogManager
    global _FileLogManager
    global _LogOptionsManager
    global _LogManager

    import logging

    from .console_log_manager import ConsoleLogManager
    from .file_log_manager import FileLogManager
    from .log_options_manager import LogOptionsManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager

    _logging = logging
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _ConsoleLogManager = ConsoleLogManager().get_singleton
    _FileLogManager = FileLogManager().get_singleton
    _LogOptionsManager = LogOptionsManager().get_singleton

    class __LogManager:
        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _FileLogManager()
                _ConsoleLogManager()
                _LogOptionsManager()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def log(
            self,
            message,
            console_options,
            file_options,
        ):
            _ConsoleLogManager().log(
                message,
                console_options,
            )

            _FileLogManager().log(
                message,
                file_options,
            )

            return message

        def log_debug(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    _ConsoleLogManager().options,
                    log_level=_logging.DEBUG,
                ),
                _LogOptionsManager().generate_modified_defaults(
                    _FileLogManager().options,
                    log_level=_logging.DEBUG,
                ),
            )

        def log_info(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    _ConsoleLogManager().options,
                    log_level=_logging.INFO,
                ),
                _LogOptionsManager().generate_modified_defaults(
                    _FileLogManager().options,
                    log_level=_logging.INFO,
                ),
            )

        def log_warning(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    _ConsoleLogManager().options,
                    log_level=_logging.WARNING,
                ),
                _LogOptionsManager().generate_modified_defaults(
                    _FileLogManager().options,
                    log_level=_logging.WARNING,
                ),
            )

        def log_error(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    _ConsoleLogManager().options,
                    log_level=_logging.ERROR,
                ),
                _LogOptionsManager().generate_modified_defaults(
                    _FileLogManager().options,
                    log_level=_logging.ERROR,
                ),
            )

        def log_critical(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    _ConsoleLogManager().options,
                    log_level=_logging.CRITICAL,
                ),
                _LogOptionsManager().generate_modified_defaults(
                    _FileLogManager().options,
                    log_level=_logging.CRITICAL,
                ),
            )

        def shutdown(self):
            _FileLogManager().shutdown()

            return True

    _LogManager = __LogManager
    _allocate_module = lambda: None


def LogManager():
    if _LogManager is None:
        _allocate_module()

    return _LogManager


# LogManager()
