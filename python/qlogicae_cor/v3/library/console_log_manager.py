__all__ = (
    "ConsoleLogManager",
)

_logging = None
_PythonRuntimeUtilityManager = None
_LogFormat = None
_LogOptions = None
_LogOptionsManager = None
_ConsoleLogManager = None


def _allocate_module():
    global _allocate_module
    global _logging
    global _PythonRuntimeUtilityManager
    global _LogFormat
    global _LogOptions
    global _LogOptionsManager
    global _ConsoleLogManager

    import logging

    from .log_format import LogFormat
    from .log_options import LogOptions
    from .log_options_manager import LogOptionsManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager

    _logging = logging
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _LogFormat = LogFormat()
    _LogOptions = LogOptions()
    _LogOptionsManager = LogOptionsManager().get_singleton

    class __ConsoleLogManager:
        __slots__ = (
            "_logger",
            "_options",
        )

        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _LogOptionsManager()

            self._logger = _logging.getLogger("console-logger")
            self._logger.setLevel(_logging.DEBUG)
            self._logger.propagate = False
            self._logger.handlers.clear()

            handler = _logging.StreamHandler()
            handler.setFormatter(_LogFormat())

            self._logger.addHandler(handler)

            self._options = _LogOptions()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def options(self):
            return self._options

        @options.setter
        def options(self, value):
            self._options = value

        def log(self, message, options):
            if not options.is_enabled:
                return ""

            message = str(message).strip()

            if options.is_verbose_enabled:
                self._logger.log(
                    options.log_level,
                    message,
                    stacklevel=options.stack_level,
                )
            else:
                print(message)

            return message

        def log_debug(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.DEBUG,
                ),
            )

        def log_info(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.INFO,
                ),
            )

        def log_warning(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.WARNING,
                ),
            )

        def log_error(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.ERROR,
                ),
            )

        def log_critical(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.CRITICAL,
                ),
            )

    _ConsoleLogManager = __ConsoleLogManager
    _allocate_module = lambda: None


def ConsoleLogManager():
    if _ConsoleLogManager is None:
        _allocate_module()

    return _ConsoleLogManager


# ConsoleLogManager()
