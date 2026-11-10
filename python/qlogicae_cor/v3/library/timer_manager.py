__all__ = (
    "TimerManager",
)

_TimeManager = None
_TimeUnit = None
_TimerManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _TimerManager

    class __TimerManager:
        __slots__ = (
            "_start_timestamp",
            "_stop_timestamp",
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
        def start_timestamp(self):
            return self._start_timestamp

        @property
        def stop_timestamp(self):
            return self._stop_timestamp

        def construct(self):
            global _TimeManager
            global _TimeUnit
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _TimeManager = (
                _ExternalDependencyManager().import_module(
                    path=".time_manager",
                    package="qlogicae_cor.v3.library",
                    member="TimeManager",
                    is_member_callable=True,
                )
            )
            _TimeUnit = (
                _ExternalDependencyManager().import_module(
                    path=".time_unit",
                    package="qlogicae_cor.v3.library",
                    member="TimeUnit",
                    is_member_callable=True,
                )
            )

            self._start_timestamp = 0
            self._stop_timestamp = 0

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def start_time(self):
            self._start_timestamp = (
                _TimeManager().get_singleton().current_nanosecond
            )

            return True

        def stop_time(self):
            self._stop_timestamp = (
                _TimeManager().get_singleton().current_nanosecond
            )

            return True

        def clear_time(self):
            self._start_timestamp = 0
            self._stop_timestamp = 0

            return True

        def reset_time(self):
            self._start_timestamp = (
                _TimeManager().get_singleton().current_nanosecond
            )
            self._stop_timestamp = 0

            return True

        def calculate_elapsed_time(self, time_unit=None):
            if time_unit is None:
                time_unit = _TimeUnit().SECOND

            TimeManager = (
                _TimeManager().get_singleton()
            )

            value = (
                TimeManager.convert_time_unit(
                    TimeManager.current_nanosecond - self._start_timestamp,
                    output_time_unit=time_unit,
                )
            )

            return value

        def calculate_duration_time(self, time_unit=None):
            if time_unit is None:
                time_unit = _TimeUnit().SECOND

            value = _TimeManager().get_singleton().convert_time_unit(
                self._stop_timestamp - self._start_timestamp,
                output_time_unit=time_unit,
            )

            return value

    _TimerManager = __TimerManager
    _allocate = lambda: None


def TimerManager():
    if _TimerManager is None:
        _allocate()

    return _TimerManager


# TimerManager()
