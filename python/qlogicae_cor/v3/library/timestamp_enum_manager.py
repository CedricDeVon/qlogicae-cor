__all__ = (
    "TimestampEnumManager",
)

_EnumConversionValue = None
_Timestamp = None
_TimestampEnumManager = None


def _allocate_module():
    global _allocate_module
    global _EnumConversionValue
    global _Timestamp
    global _TimestampEnumManager

    from .enum_conversion_value import EnumConversionValue
    from .timestamp import Timestamp

    _EnumConversionValue = EnumConversionValue()
    _Timestamp = Timestamp()

    class __TimestampEnumManager:
        _singleton = None

        def __init__(self):
            pass

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
                output_type = _EnumConversionValue.STRING

            match output_type:
                case _EnumConversionValue.STRING:
                    match input_type:
                        case _Timestamp.ISO_DATE_STRING:
                            return "iso_date_string"

                        case _Timestamp.ISO_FILESYSTEM_STRING:
                            return "iso_filesystem_string"

                        case _:
                            return "iso_date_string"

                case _EnumConversionValue.ENUM:
                    match input_type.lower():
                        case "local":
                            return _Timestamp.ISO_DATE_STRING

                        case "iso_filesystem_string":
                            return _Timestamp.ISO_FILESYSTEM_STRING

                        case _:
                            return _Timestamp.NONE

                case _:
                    return _EnumConversionValue.NONE

    _TimestampEnumManager = __TimestampEnumManager
    _allocate_module = lambda: None


def TimestampEnumManager():
    if _TimestampEnumManager is None:
        _allocate_module()

    return _TimestampEnumManager


# TimestampEnumManager()
