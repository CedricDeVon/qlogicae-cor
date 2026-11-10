__all__ = (
    "LogManager",
)

_logging = None
_ConsoleLogManager = None
_FileLogManager = None
_LogOptionsManager = None
_LogManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _LogManager

    class __LogManager:
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

        def construct(self):
            global _ExternalDependencyManager
            global _logging
            global _ConsoleLogManager
            global _FileLogManager
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
            _ConsoleLogManager = (
                _ExternalDependencyManager().import_module(
                    path=".console_log_manager",
                    package="qlogicae_cor.v3.library",
                    member="ConsoleLogManager",
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
            _LogOptionsManager = (
                _ExternalDependencyManager().import_module(
                    path=".log_options_manager",
                    package="qlogicae_cor.v3.library",
                    member="LogOptionsManager",
                    is_member_callable=True,
                )
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            _ConsoleLogManager().get_singleton().shutdown()
            _FileLogManager().get_singleton().shutdown()

            return True

        def log(
            self,
            message,
            console_options,
            file_options,
        ):
            _ConsoleLogManager().get_singleton().log(
                message,
                console_options,
            )

            _FileLogManager().get_singleton().log(
                message,
                file_options,
            )

            return message

        def log_debug(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _ConsoleLogManager().get_singleton().options,
                    log_level=_logging().DEBUG,
                ),
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _FileLogManager().get_singleton().options,
                    log_level=_logging().DEBUG,
                ),
            )

        def log_info(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _ConsoleLogManager().get_singleton().options,
                    log_level=_logging().INFO,
                ),
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _FileLogManager().get_singleton().options,
                    log_level=_logging().INFO,
                ),
            )

        def log_warning(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _ConsoleLogManager().get_singleton().options,
                    log_level=_logging().WARNING,
                ),
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _FileLogManager().get_singleton().options,
                    log_level=_logging().WARNING,
                ),
            )

        def log_error(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _ConsoleLogManager().get_singleton().options,
                    log_level=_logging().ERROR,
                ),
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _FileLogManager().get_singleton().options,
                    log_level=_logging().ERROR,
                ),
            )

        def log_critical(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _ConsoleLogManager().get_singleton().options,
                    log_level=_logging().CRITICAL,
                ),
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    _FileLogManager().get_singleton().options,
                    log_level=_logging().CRITICAL,
                ),
            )

    _LogManager = __LogManager
    _allocate = lambda: None


def LogManager():
    if _LogManager is None:
        _allocate()

    return _LogManager


# LogManager()
