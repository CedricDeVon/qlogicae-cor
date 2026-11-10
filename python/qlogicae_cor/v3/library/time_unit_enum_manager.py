__all__ = (
    "TimeUnitEnumManager",
)

_EnumConversionValue = None
_TimeUnit = None
_TimeUnitEnumManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _TimeUnitEnumManager

    class __TimeUnitEnumManager:
        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _EnumConversionValue
            global _TimeUnit
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _EnumConversionValue = (
                _ExternalDependencyManager().import_module(
                    path=".enum_conversion_value",
                    package="qlogicae_cor.v3.library",
                    member="EnumConversionValue",
                    is_member_callable=True
                )
            )
            _TimeUnit = (
                _ExternalDependencyManager().import_module(
                    path=".time_unit",
                    package="qlogicae_cor.v3.library",
                    member="TimeUnit",
                    is_member_callable=True
                )
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def convert_value(
            self,
            input_type,
            output_type=None,
        ):
            EnumConversionValue = (
                _EnumConversionValue()
            )
            TimeUnit = (
                _TimeUnit()
            )

            if output_type is None:
                output_type = EnumConversionValue.STRING

            match output_type:
                case EnumConversionValue.STRING:
                    match input_type:
                        case TimeUnit.NANOSECOND:
                            return "nanosecond"

                        case TimeUnit.MICROSECOND:
                            return "microsecond"

                        case TimeUnit.MILLISECOND:
                            return "millisecond"

                        case TimeUnit.SECOND:
                            return "second"

                        case TimeUnit.MINUTE:
                            return "minute"

                        case TimeUnit.HOUR:
                            return "hour"

                        case TimeUnit.DAY:
                            return "day"

                        case TimeUnit.WEEK:
                            return "week"

                        case TimeUnit.MONTH:
                            return "month"

                        case TimeUnit.YEAR:
                            return "year"

                        case TimeUnit.DECADE:
                            return "decade"

                        case TimeUnit.CENTURY:
                            return "century"

                        case TimeUnit.MILLENNIUM:
                            return "millennium"

                        case _:
                            return "none"

                case EnumConversionValue.ENUM:
                    match str(input_type).lower():
                        case "nanosecond" | "ns":
                            return TimeUnit.NANOSECOND

                        case "microsecond" | "us":
                            return TimeUnit.MICROSECOND

                        case "millisecond" | "ms":
                            return TimeUnit.MILLISECOND

                        case "second" | "sec":
                            return TimeUnit.SECOND

                        case "minute" | "min":
                            return TimeUnit.MINUTE

                        case "hour" | "hr":
                            return TimeUnit.HOUR

                        case "day" | "d":
                            return TimeUnit.DAY

                        case "week" | "wk":
                            return TimeUnit.WEEK

                        case "month" | "mon":
                            return TimeUnit.MONTH

                        case "year" | "yr":
                            return TimeUnit.YEAR

                        case "decade" | "deca":
                            return TimeUnit.DECADE

                        case "century" | "cen":
                            return TimeUnit.CENTURY

                        case "millennium" | "mil":
                            return TimeUnit.MILLENNIUM

                        case _:
                            return TimeUnit.NONE

                case _:
                    return EnumConversionValue.NONE

    _TimeUnitEnumManager = __TimeUnitEnumManager
    _allocate = lambda: None


def TimeUnitEnumManager():
    if _TimeUnitEnumManager is None:
        _allocate()

    return _TimeUnitEnumManager


# TimeUnitEnumManager()
