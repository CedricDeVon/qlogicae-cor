__all__ = (
    "TimeUnitEnumManager",
)

_EnumConversionValue = None
_TimeUnit = None
_TimeUnitEnumManager = None


def _allocate_module():
    global _allocate_module
    global _EnumConversionValue
    global _TimeUnit
    global _TimeUnitEnumManager

    from .enum_conversion_value import EnumConversionValue
    from .time_unit import TimeUnit

    _EnumConversionValue = EnumConversionValue()
    _TimeUnit = TimeUnit()

    class __TimeUnitEnumManager:
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
                        case _TimeUnit.NANOSECOND:
                            return "nanosecond"

                        case _TimeUnit.MICROSECOND:
                            return "microsecond"

                        case _TimeUnit.MILLISECOND:
                            return "millisecond"

                        case _TimeUnit.SECOND:
                            return "second"

                        case _TimeUnit.MINUTE:
                            return "minute"

                        case _TimeUnit.HOUR:
                            return "hour"

                        case _TimeUnit.DAY:
                            return "day"

                        case _TimeUnit.WEEK:
                            return "week"

                        case _TimeUnit.MONTH:
                            return "month"

                        case _TimeUnit.YEAR:
                            return "year"

                        case _TimeUnit.DECADE:
                            return "decade"

                        case _TimeUnit.CENTURY:
                            return "century"

                        case _TimeUnit.MILLENNIUM:
                            return "millennium"

                        case _:
                            return "none"

                case _EnumConversionValue.ENUM:
                    match str(input_type).lower():
                        case "nanosecond" | "ns":
                            return _TimeUnit.NANOSECOND

                        case "microsecond" | "us":
                            return _TimeUnit.MICROSECOND

                        case "millisecond" | "ms":
                            return _TimeUnit.MILLISECOND

                        case "second" | "sec":
                            return _TimeUnit.SECOND

                        case "minute" | "min":
                            return _TimeUnit.MINUTE

                        case "hour" | "hr":
                            return _TimeUnit.HOUR

                        case "day" | "d":
                            return _TimeUnit.DAY

                        case "week" | "wk":
                            return _TimeUnit.WEEK

                        case "month" | "mon":
                            return _TimeUnit.MONTH

                        case "year" | "yr":
                            return _TimeUnit.YEAR

                        case "decade" | "deca":
                            return _TimeUnit.DECADE

                        case "century" | "cen":
                            return _TimeUnit.CENTURY

                        case "millennium" | "mil":
                            return _TimeUnit.MILLENNIUM

                        case _:
                            return _TimeUnit.NONE

                case _:
                    return _EnumConversionValue.NONE

    _TimeUnitEnumManager = __TimeUnitEnumManager
    _allocate_module = lambda: None


def TimeUnitEnumManager():
    if _TimeUnitEnumManager is None:
        _allocate_module()

    return _TimeUnitEnumManager


# TimeUnitEnumManager()
