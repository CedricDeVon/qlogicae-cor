__all__ = (
    "TimerManager",
)

_PythonRuntimeUtilityManager = None
_TimeManager = None
_TimeUnit = None
_TimerManager = None


def _allocate_module():
    global _allocate_module
    global _PythonRuntimeUtilityManager
    global _TimeManager
    global _TimeUnit
    global _TimerManager

    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .time_manager import TimeManager
    from .time_unit import TimeUnit

    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _TimeManager = TimeManager().get_singleton
    _TimeUnit = TimeUnit()

    class __TimerManager:
        __slots__ = (
            "_start_timestamp",
            "_stop_timestamp",
        )

        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _TimeManager()

            self._start_timestamp = 0
            self._stop_timestamp = 0

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def start_timestamp(self):
            return self._start_timestamp

        @property
        def stop_timestamp(self):
            return self._stop_timestamp

        def start_time(self):
            self._start_timestamp = _TimeManager().current_nanosecond

            return True

        def stop_time(self):
            self._stop_timestamp = _TimeManager().current_nanosecond

            return True

        def clear_time(self):
            self._start_timestamp = 0
            self._stop_timestamp = 0

            return True

        def reset_time(self):
            self._start_timestamp = _TimeManager().current_nanosecond
            self._stop_timestamp = 0

            return True

        def calculate_elapsed_time(self, time_unit=None):
            if time_unit is None:
                time_unit = _TimeUnit.SECOND

            value = _TimeManager().convert_time_unit(
                _TimeManager().current_nanosecond - self._start_timestamp,
                output_time_unit=time_unit,
            )

            return value

        def calculate_duration_time(self, time_unit=None):
            if time_unit is None:
                time_unit = _TimeUnit.SECOND

            value = _TimeManager().convert_time_unit(
                self._stop_timestamp - self._start_timestamp,
                output_time_unit=time_unit,
            )

            return value

    _TimerManager = __TimerManager
    _allocate_module = lambda: None


def TimerManager():
    if _TimerManager is None:
        _allocate_module()

    return _TimerManager


# TimerManager()
