__all__ = (
    "TimeZoneEnumManager",
)

_datetime = None
_EnumConversionValue = None
_TimeZone = None
_TimeZoneEnumManager = None
_ExternalDependencyManager = None

def _allocate():
    global _allocate
    global _TimeZoneEnumManager

    class __TimeZoneEnumManager:
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
            global _datetime
            global _EnumConversionValue
            global _TimeZone

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _datetime = (
                _ExternalDependencyManager().import_module(
                    path="datetime",
                )
            )
            _EnumConversionValue = (
                _ExternalDependencyManager().import_module(
                    path=".enum_conversion_value",
                    package="qlogicae_cor.v3.library",
                    member="EnumConversionValue",
                    is_member_callable=True,
                )
            )
            _TimeZone = (
                _ExternalDependencyManager().import_module(
                    path=".time_zone",
                    package="qlogicae_cor.v3.library",
                    member="TimeZone",
                    is_member_callable=True,
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
            TimeZone = (
                _TimeZone()
            )
            EnumConversionValue = (
                _EnumConversionValue()
            )

            if output_type is None:
                output_type = EnumConversionValue.STRING

            match output_type:
                case EnumConversionValue.STRING:
                    match input_type:
                        case TimeZone.LOCAL:
                            return "local"

                        case TimeZone.UTC:
                            return "utc"

                        case TimeZone.CUSTOM:
                            return "custom"

                        case _:
                            return "local"

                case EnumConversionValue.ENUM:
                    match str(input_type).lower():
                        case "local":
                            return TimeZone.LOCAL

                        case "utc":
                            return TimeZone.UTC

                        case "custom":
                            return TimeZone.CUSTOM

                        case _:
                            return TimeZone.LOCAL

                case EnumConversionValue.CUSTOM:
                    match str(input_type).lower():
                        case "local":
                            return _datetime().datetime.now().astimezone().tzinfo

                        case "utc":
                            return _datetime().UTC

                        case "custom":
                            return _datetime().datetime.now().astimezone().tzinfo

                        case _:
                            return _datetime().datetime.now().astimezone().tzinfo

                case _:
                    return EnumConversionValue.NONE

    _TimeZoneEnumManager = __TimeZoneEnumManager
    _allocate = lambda: None


def TimeZoneEnumManager():
    if _TimeZoneEnumManager is None:
        _allocate()

    return _TimeZoneEnumManager

# TimeZoneEnumManager()
