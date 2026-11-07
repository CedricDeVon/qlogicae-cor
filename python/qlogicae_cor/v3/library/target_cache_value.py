__all__ = (
    "TargetCacheValue",
)

_TargetCacheValue = None


def _allocate():
    global _allocate
    global _TargetCacheValue

    from enum import Enum

    class __TargetCacheValue(Enum):
        ANY = 0
        FILESYSTEM_PATH = 1
        FILE_PATH = 2
        FOLDER_PATH = 3
        DEFINED = 4
        NONE = 5

    _TargetCacheValue = __TargetCacheValue
    _allocate = lambda: None


def TargetCacheValue():
    if _TargetCacheValue is None:
        _allocate()

    return _TargetCacheValue
