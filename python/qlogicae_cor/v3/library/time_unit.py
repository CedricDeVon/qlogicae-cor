__all__ = (
    "TimeUnit",
)

_TimeUnit = None


def _allocate_module():
    global _allocate_module
    global _TimeUnit

    from enum import Enum

    class __TimeUnit(Enum):
        NANOSECOND = 0
        MICROSECOND = 1
        MILLISECOND = 2
        SECOND = 3
        MINUTE = 4
        HOUR = 5
        DAY = 6
        WEEK = 7
        MONTH = 8
        YEAR = 9
        DECADE = 10
        CENTURY = 11
        MILLENNIUM = 12
        NONE = 13

    _TimeUnit = __TimeUnit
    _allocate_module = lambda: None


def TimeUnit():
    if _TimeUnit is None:
        _allocate_module()

    return _TimeUnit


# TimeUnit()
