__all__ = (
    "LogFormat",
)

_logging = None
_PythonRuntimeUtilityManager = None
_TimestampManager = None
_LogFormat = None


def _allocate_module():
    global _allocate_module
    global _logging
    global _PythonRuntimeUtilityManager
    global _TimestampManager
    global _LogFormat

    import logging

    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .timestamp_manager import TimestampManager

    _logging = logging
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _TimestampManager = TimestampManager().get_singleton

    class __LogFormat(_logging.Formatter):
        def __init__(self):
            super().__init__()

            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _TimestampManager()

        def format(self, record):
            timestamp = (
                _TimestampManager().generate_current_timestamp()
            )

            return (
                f"[ {timestamp} ] "
                f"[ {record.levelname} ] "
                f"{record.getMessage()}"
            )

    _LogFormat = __LogFormat
    _allocate_module = lambda: None


def LogFormat():
    if _LogFormat is None:
        _allocate_module()

    return _LogFormat


# LogFormat()
