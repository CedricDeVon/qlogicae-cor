__all__ = (
    "TimestampManager",
)

_time = None
_UTC = None
_datetime = None
_PythonRuntimeUtilityManager = None
_TimeUnit = None
_TimeZoneManager = None
_Timestamp = None
_TimestampManager = None


def _allocate_module():
    global _allocate_module
    global _time
    global _UTC
    global _datetime
    global _PythonRuntimeUtilityManager
    global _TimeUnit
    global _TimeZoneManager
    global _Timestamp
    global _TimestampManager

    import time
    from datetime import UTC, datetime

    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .time_unit import TimeUnit
    from .time_zone_manager import TimeZoneManager
    from .timestamp import Timestamp

    _time = time
    _UTC = UTC
    _datetime = datetime
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _TimeUnit = TimeUnit
    _TimeZoneManager = TimeZoneManager().get_singleton
    _Timestamp = Timestamp

    class __TimestampManager:
        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _TimeZoneManager()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def generate_current_timestamp(
            self,
            timestamp=None,
            time_unit=None,
        ):
            if timestamp is None:
                timestamp = _Timestamp.ISO_DATE_STRING

            if time_unit is None:
                time_unit = _TimeUnit.NANOSECOND

            timestamp_nanoseconds = _time.time_ns()

            current = _datetime.fromtimestamp(
                timestamp_nanoseconds / 1_000_000_000,
                _TimeZoneManager().selected_time_zone,
            )

            match time_unit:
                case (
                    _TimeUnit.NONE
                    | _TimeUnit.SECOND
                ):
                    fraction = ""

                case _TimeUnit.MILLISECOND:
                    fraction = (
                        f".{timestamp_nanoseconds // 1_000_000 % 1_000:03d}"
                    )

                case _TimeUnit.MICROSECOND:
                    fraction = (
                        f".{timestamp_nanoseconds // 1_000 % 1_000_000:06d}"
                    )

                case _TimeUnit.NANOSECOND:
                    fraction = (
                        f".{timestamp_nanoseconds % 1_000_000_000:09d}"
                    )

                case _:
                    fraction = ""

            if current.tzinfo is _UTC:
                suffix = "Z"
            else:
                suffix = current.strftime("%z")

                if suffix:
                    suffix = f"{suffix[:-2]}:{suffix[-2:]}"

            match timestamp:
                case _Timestamp.ISO_DATE_STRING:
                    prefix = current.strftime("%Y-%m-%dT%H:%M:%S")

                case _Timestamp.ISO_FILESYSTEM_STRING:
                    prefix = current.strftime("%Y-%m-%dT%H-%M-%S")
                    suffix = suffix.replace(":", "-")

                case _:
                    return ""

            return "".join(
                (
                    prefix,
                    fraction,
                    suffix,
                )
            )

    _TimestampManager = __TimestampManager
    _allocate_module = lambda: None


def TimestampManager():
    if _TimestampManager is None:
        _allocate_module()

    return _TimestampManager


# TimestampManager()
