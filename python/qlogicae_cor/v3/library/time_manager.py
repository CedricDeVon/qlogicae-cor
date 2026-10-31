__all__ = (
    "TimeManager",
)

_time = None
_date = None
_datetime = None
_TimeUnit = None
_PythonRuntimeUtilityManager = None
_TimeZoneManager = None
_TimeManager = None


def _allocate_module():
    global _allocate_module
    global _time
    global _date
    global _datetime
    global _TimeUnit
    global _PythonRuntimeUtilityManager
    global _TimeZoneManager
    global _TimeManager

    import time
    from datetime import date, datetime

    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .time_unit import TimeUnit
    from .time_zone_manager import TimeZoneManager

    _time = time
    _date = date
    _datetime = datetime
    _TimeUnit = TimeUnit()
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _TimeZoneManager = TimeZoneManager().get_singleton

    class __TimeManager:
        __slots__ = (
            "_TIME_UNIT_TO_NANOSECONDS",
        )

        _singleton = None

        def __init__(self):
            if (
                _PythonRuntimeUtilityManager
                .is_allocated_during_object_construction
            ):
                _TimeZoneManager()

            self._TIME_UNIT_TO_NANOSECONDS = {
                _TimeUnit.NANOSECOND: 1.0,
                _TimeUnit.MICROSECOND: 1e3,
                _TimeUnit.MILLISECOND: 1e6,
                _TimeUnit.SECOND: 1e9,
                _TimeUnit.MINUTE: 60e9,
                _TimeUnit.HOUR: 3600e9,
                _TimeUnit.DAY: 86400e9,
                _TimeUnit.WEEK: 604800e9,
                _TimeUnit.MONTH: 2629746e9,
                _TimeUnit.YEAR: 31556952e9,
                _TimeUnit.DECADE: 315569520e9,
                _TimeUnit.CENTURY: 3155695200e9,
                _TimeUnit.MILLENNIUM: 31556952000e9,
            }

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def current_iso8601_date(self):
            return _date.today().strftime(
                "%Y-%m-%d",
            )

        @property
        def current_nanosecond(self):
            return _time.time_ns()

        @property
        def current_microsecond(self):
            return self.current_nanosecond // 1_000

        @property
        def current_millisecond(self):
            return self.current_nanosecond // 1_000_000

        @property
        def current_second(self):
            return _datetime.now(
                _TimeZoneManager().selected_time_zone,
            ).second

        @property
        def current_minute(self):
            return _datetime.now(
                _TimeZoneManager().selected_time_zone,
            ).minute

        @property
        def current_hour(self):
            return _datetime.now(
                _TimeZoneManager().selected_time_zone,
            ).hour

        @property
        def current_day(self):
            return _datetime.now(
                _TimeZoneManager().selected_time_zone,
            ).day

        @property
        def current_week(self):
            return _datetime.now().isocalendar().week

        @property
        def current_month(self):
            return _datetime.now(
                _TimeZoneManager().selected_time_zone,
            ).month

        @property
        def current_year(self):
            return _datetime.now(
                _TimeZoneManager().selected_time_zone,
            ).year

        @property
        def current_decade(self):
            return self.current_year // 10

        @property
        def current_century(self):
            return (
                self.current_year - 1
            ) // 100 + 1

        @property
        def current_millenium(self):
            return (
                self.current_year - 1
            ) // 1000 + 1

        def calculate_elapsed_time(
            self,
            start,
            time_unit=None,
        ):
            if time_unit is None:
                time_unit = _TimeUnit.SECOND

            return self.convert_time_unit(
                _time.time_ns() - start,
                _TimeUnit.NANOSECOND,
                time_unit,
            )

        def calculate_duration_time(
            self,
            start,
            end,
            time_unit=None,
        ):
            if time_unit is None:
                time_unit = _TimeUnit.SECOND

            return self.convert_time_unit(
                end - start,
                _TimeUnit.NANOSECOND,
                time_unit,
            )

        def convert_time_unit(
            self,
            value,
            input_time_unit=None,
            output_time_unit=None,
        ):
            if input_time_unit is None:
                input_time_unit = _TimeUnit.SECOND

            if output_time_unit is None:
                output_time_unit = _TimeUnit.SECOND

            if input_time_unit is output_time_unit:
                return float(value)

            nanoseconds = (
                value
                * self._TIME_UNIT_TO_NANOSECONDS[input_time_unit]
            )

            return (
                nanoseconds
                / self._TIME_UNIT_TO_NANOSECONDS[output_time_unit]
            )

    _TimeManager = __TimeManager
    _allocate_module = lambda: None


def TimeManager():
    if _TimeManager is None:
        _allocate_module()

    return _TimeManager


# TimeManager()
