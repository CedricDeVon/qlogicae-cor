__all__ = (
    "TargetCacheValue",
)

_TargetCacheValue = None


def _allocate_module():
    global _allocate_module
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
    _allocate_module = lambda: None


def TargetCacheValue():
    if _TargetCacheValue is None:
        _allocate_module()

    return _TargetCacheValue


# TargetCacheValue()
