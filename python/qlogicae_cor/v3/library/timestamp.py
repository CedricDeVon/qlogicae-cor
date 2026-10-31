__all__ = (
    "Timestamp",
)

_Timestamp = None


def _allocate_module():
    global _allocate_module
    global _Timestamp

    from enum import Enum

    class __Timestamp(Enum):
        ISO_DATE_STRING = 0
        ISO_FILESYSTEM_STRING = 1
        NONE = 2

    _Timestamp = __Timestamp
    _allocate_module = lambda: None


def Timestamp():
    if _Timestamp is None:
        _allocate_module()

    return _Timestamp


# Timestamp()
