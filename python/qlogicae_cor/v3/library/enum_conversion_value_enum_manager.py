__all__ = (
    "EnumConversionValueEnumManager",
)

_enum_conversion_value = None
_EnumConversionValueEnumManager = None


def _allocate_module():
    global _allocate_module
    global _enum_conversion_value
    global _EnumConversionValueEnumManager

    from .enum_conversion_value import EnumConversionValue

    _enum_conversion_value = EnumConversionValue()

    class __EnumConversionValueEnumManager:
        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def convert_value(
            self,
            input_type,
            output_type=None,
        ):
            if output_type is None:
                output_type = _enum_conversion_value.STRING

            match output_type:
                case _enum_conversion_value.STRING:
                    match input_type:
                        case _enum_conversion_value.STRING:
                            return "string"

                        case _enum_conversion_value.ENUM:
                            return "enum"

                        case _enum_conversion_value.CUSTOM:
                            return "custom"

                        case _:
                            return "none"

                case _enum_conversion_value.ENUM:
                    match str(input_type).lower():
                        case "string":
                            return _enum_conversion_value.STRING

                        case "none":
                            return _enum_conversion_value.ENUM

                        case "custom":
                            return _enum_conversion_value.CUSTOM

                        case _:
                            return _enum_conversion_value.NONE

                case _:
                    return _enum_conversion_value.NONE

    _EnumConversionValueEnumManager = __EnumConversionValueEnumManager
    _allocate_module = lambda: None


def EnumConversionValueEnumManager():
    if _EnumConversionValueEnumManager is None:
        _allocate_module()

    return _EnumConversionValueEnumManager


# EnumConversionValueEnumManager()
