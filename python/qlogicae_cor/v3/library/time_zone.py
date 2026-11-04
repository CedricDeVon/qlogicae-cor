__all__ = (
    "TimeZone",
)

_TimeZone = None


def _allocate():
    global _allocate
    global _TimeZone

    from enum import Enum

    class __TimeZone(Enum):
        UTC = 0
        LOCAL = 1
        CUSTOM = 2
        NONE = 3

    _TimeZone = __TimeZone
    _allocate = lambda: None


def TimeZone():
    if _TimeZone is None:
        _allocate()

    return _TimeZone


# TimeZone()
