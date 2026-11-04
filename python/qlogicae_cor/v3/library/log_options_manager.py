__all__ = (
    "LogOptionsManager",
)

_logging = None
_LogOptions = None
_LogOptionsManager = None


def _allocate():
    global _allocate
    global _LogOptionsManager

    class __LogOptionsManager:
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
            global _logging
            global _LogOptions

            import logging

            from .log_options import LogOptions

            _logging = logging
            _LogOptions = LogOptions

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True

        def generate_modified_defaults(
            self,
            default_log_options,
            log_level=None,
        ):
            if log_level is None:
                log_level = _logging.DEBUG

            value = _LogOptions(
                is_enabled=default_log_options.is_enabled,
                is_verbose_enabled=(
                    default_log_options.is_verbose_enabled
                ),
                log_level=log_level,
                stack_level=default_log_options.stack_level,
            )

            return value

    _LogOptionsManager = __LogOptionsManager
    _allocate = lambda: None


def LogOptionsManager():
    if _LogOptionsManager is None:
        _allocate()

    return _LogOptionsManager


# LogOptionsManager()
