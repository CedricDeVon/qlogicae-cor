__all__ = (
    "TimeZoneManager",
)

_PythonRuntimeUtilityManager = None
_EnumConversionValue = None
_TimeZoneEnumManager = None
_TimeZoneManager = None


def _allocate_module():
    global _allocate_module
    global _PythonRuntimeUtilityManager
    global _EnumConversionValue
    global _TimeZoneEnumManager
    global _TimeZoneManager

    from .enum_conversion_value import EnumConversionValue
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .time_zone_enum_manager import TimeZoneEnumManager

    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _EnumConversionValue = EnumConversionValue()
    _TimeZoneEnumManager = TimeZoneEnumManager().get_singleton

    class __TimeZoneManager:
        __slots__ = (
            "_selected_time_zone_type",
            "_valid_time_zone_types",
        )

        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _TimeZoneEnumManager()

            self._selected_time_zone_type = "local"
            self._valid_time_zone_types = {
                "local",
                "utc",
            }

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def selected_time_zone_type(self):
            return self._selected_time_zone_type

        @selected_time_zone_type.setter
        def selected_time_zone_type(self, value):
            if value not in self._valid_time_zone_types:
                raise ValueError(
                    "time zones must include the followwing: "
                    f"{self._valid_time_zone_types}",
                )

            self._selected_time_zone_type = value

        @property
        def selected_time_zone(self):
            return _TimeZoneEnumManager().convert_value(
                self._selected_time_zone_type,
                _EnumConversionValue.CUSTOM,
            )

    _TimeZoneManager = __TimeZoneManager
    _allocate_module = lambda: None


def TimeZoneManager():
    if _TimeZoneManager is None:
        _allocate_module()

    return _TimeZoneManager


# TimeZoneManager()
