__all__ = (
    "TimeZoneEnumManager",
)

_datetime = None
_UTC = None
_EnumConversionValue = None
_TimeZone = None
_TimeZoneEnumManager = None


def _allocate_module():
    global _allocate_module
    global _datetime
    global _UTC
    global _EnumConversionValue
    global _TimeZone
    global _TimeZoneEnumManager

    from datetime import UTC, datetime

    from .enum_conversion_value import EnumConversionValue
    from .time_zone import TimeZone

    _datetime = datetime
    _UTC = UTC
    _EnumConversionValue = EnumConversionValue()
    _TimeZone = TimeZone()

    class __TimeZoneEnumManager:
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
                output_type = _EnumConversionValue.STRING

            match output_type:
                case _EnumConversionValue.STRING:
                    match input_type:
                        case _TimeZone.LOCAL:
                            return "local"

                        case _TimeZone.UTC:
                            return "utc"

                        case _TimeZone.CUSTOM:
                            return "custom"

                        case _:
                            return "local"

                case _EnumConversionValue.ENUM:
                    match str(input_type).lower():
                        case "local":
                            return _TimeZone.LOCAL

                        case "utc":
                            return _TimeZone.UTC

                        case "custom":
                            return _TimeZone.CUSTOM

                        case _:
                            return _TimeZone.LOCAL

                case _EnumConversionValue.CUSTOM:
                    match str(input_type).lower():
                        case "local":
                            return _datetime.now().astimezone().tzinfo

                        case "utc":
                            return _UTC

                        case "custom":
                            return _datetime.now().astimezone().tzinfo

                        case _:
                            return _datetime.now().astimezone().tzinfo

                case _:
                    return _EnumConversionValue.NONE

    _TimeZoneEnumManager = __TimeZoneEnumManager
    _allocate_module = lambda: None


def TimeZoneEnumManager():
    if _TimeZoneEnumManager is None:
        _allocate_module()

    return _TimeZoneEnumManager

# TimeZoneEnumManager()
