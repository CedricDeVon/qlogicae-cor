__all__ = (
    "EnumConversionValueEnumManager",
)

_enum_conversion_value = None
_EnumConversionValueEnumManager = None


def _allocate_module():
    global _allocate_module
    global _EnumConversionValueEnumManager

    class __EnumConversionValueEnumManager:
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
            global _enum_conversion_value

            from .enum_conversion_value import EnumConversionValue

            _enum_conversion_value = EnumConversionValue()

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True

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
