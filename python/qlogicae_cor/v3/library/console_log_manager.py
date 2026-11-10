__all__ = (
    "ConsoleLogManager",
)

_logging = None
_LogFormat = None
_LogOptions = None
_LogOptionsManager = None
_ConsoleLogManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _ConsoleLogManager

    class __ConsoleLogManager:
        __slots__ = (
            "_logger",
            "_options",
        )

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

        @property
        def options(self):
            return self._options

        @options.setter
        def options(self, value):
            self._options = value

        def construct(self):
            global _ExternalDependencyManager
            global _logging
            global _LogFormat
            global _LogOptions
            global _LogOptionsManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _logging = (
                _ExternalDependencyManager().import_module(
                    path="logging",
                )
            )
            _LogFormat = (
                _ExternalDependencyManager().import_module(
                    path=".log_format",
                    package="qlogicae_cor.v3.library",
                    member="LogFormat",
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
            _LogOptionsManager = (
                _ExternalDependencyManager().import_module(
                    path=".log_options_manager",
                    package="qlogicae_cor.v3.library",
                    member="LogOptionsManager",
                    is_member_callable=True,
                )
            )

            self._logger = _logging().getLogger("console-logger")
            self._logger.setLevel(_logging().DEBUG)
            self._logger.propagate = False
            self._logger.handlers.clear()

            handler = _logging().StreamHandler()
            handler.setFormatter(_LogFormat()())

            self._logger.addHandler(handler)

            self._options = _LogOptions()()

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            self._options = (
                kwargs.get(
                    "options",
                    _LogOptions()()
                ) or _LogOptions()()
            )

            return True

        def shutdown(self):
            return True

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
                _LogOptionsManager()
                    .get_singleton().generate_modified_defaults(
                        self._options,
                        log_level=_logging().DEBUG,
                    ),
            )

        def log_info(self, message):
            return self.log(
                message,
                _LogOptionsManager()
                    .get_singleton().generate_modified_defaults(
                        self._options,
                        log_level=_logging().INFO,
                    ),
            )

        def log_warning(self, message):
            return self.log(
                message,
                _LogOptionsManager()
                    .get_singleton().generate_modified_defaults(
                        self._options,
                        log_level=_logging().WARNING,
                    ),
            )

        def log_error(self, message):
            return self.log(
                message,
                _LogOptionsManager()
                    .get_singleton().generate_modified_defaults(
                        self._options,
                        log_level=_logging().ERROR,
                    ),
            )

        def log_critical(self, message):
            return self.log(
                message,
                _LogOptionsManager()
                    .get_singleton().generate_modified_defaults(
                        self._options,
                        log_level=_logging().CRITICAL,
                    ),
            )

    _ConsoleLogManager = __ConsoleLogManager
    _allocate = lambda: None


def ConsoleLogManager():
    if _ConsoleLogManager is None:
        _allocate()

    return _ConsoleLogManager


# ConsoleLogManager()
