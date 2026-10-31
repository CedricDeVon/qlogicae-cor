__all__ = (
    "LogOptionsManager",
)

_logging = None
_LogOptions = None
_LogOptionsManager = None


def _allocate_module():
    global _allocate_module
    global _logging
    global _LogOptions
    global _LogOptionsManager

    import logging

    from .log_options import LogOptions

    _logging = logging
    _LogOptions = LogOptions

    class __LogOptionsManager:
        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

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
    _allocate_module = lambda: None


def LogOptionsManager():
    if _LogOptionsManager is None:
        _allocate_module()

    return _LogOptionsManager


# LogOptionsManager()
