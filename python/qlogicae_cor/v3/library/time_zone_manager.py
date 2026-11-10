__all__ = (
    "TimeZoneManager",
)

_EnumConversionValue = None
_TimeZoneEnumManager = None
_TimeZoneManager = None
_ExternalDependencyManager = None

def _allocate():
    global _allocate
    global _TimeZoneManager

    class __TimeZoneManager:
        __slots__ = (
            "_selected_time_zone_type",
            "_valid_time_zone_types",
        )

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
            return _TimeZoneEnumManager().get_singleton().convert_value(
                self._selected_time_zone_type,
                _EnumConversionValue().CUSTOM,
            )

        def construct(self):
            global _EnumConversionValue
            global _TimeZoneEnumManager
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
                    is_member_callable=True,
                )
            )

            _TimeZoneEnumManager = (
                _ExternalDependencyManager().import_module(
                    path=".time_zone_enum_manager",
                    package="qlogicae_cor.v3.library",
                    member="TimeZoneEnumManager",
                    is_member_callable=True,
                )
            )

            self._selected_time_zone_type = (
                "local"
            )
            self._valid_time_zone_types = {
                "local",
                "utc",
            }

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True


    _TimeZoneManager = __TimeZoneManager
    _allocate = lambda: None


def TimeZoneManager():
    if _TimeZoneManager is None:
        _allocate()

    return _TimeZoneManager


# TimeZoneManager()
