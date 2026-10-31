__all__ = (
    "EnumConversionValue",
)

_EnumConversionValue = None

def _allocate_module():
    global _allocate_module
    global _EnumConversionValue

    from enum import Enum

    class __EnumConversionValue(Enum):
        STRING = 0
        ENUM = 1
        CUSTOM = 2
        NONE = 3

    _EnumConversionValue = __EnumConversionValue
    _allocate_module = lambda: None


def EnumConversionValue():
    if _EnumConversionValue is None:
        _allocate_module()

    return _EnumConversionValue

# EnumConversionValue()
