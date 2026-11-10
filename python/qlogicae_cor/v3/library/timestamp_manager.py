__all__ = (
    "TimestampManager",
)

_time = None
_datetime = None
_TimeUnit = None
_TimeZoneManager = None
_Timestamp = None
_TimestampManager = None
_ExternalDependencyManager = None

def _allocate():
    global _allocate
    global _TimestampManager

    class __TimestampManager:
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
            global _time
            global _datetime
            global _TimeUnit
            global _TimeZoneManager
            global _Timestamp
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _time = (
                _ExternalDependencyManager().import_module(
                    path="time"
                )
            )
            _datetime = (
                _ExternalDependencyManager().import_module(
                    path="datetime",
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
            _TimeZoneManager = (
                _ExternalDependencyManager().import_module(
                    path=".time_zone_manager",
                    package="qlogicae_cor.v3.library",
                    member="TimeZoneManager",
                    is_member_callable=True,
                )
            )
            _Timestamp = (
                _ExternalDependencyManager().import_module(
                    path=".timestamp",
                    package="qlogicae_cor.v3.library",
                    member="Timestamp",
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

        def generate_current_timestamp(
            self,
            timestamp=None,
            time_unit=None,
        ):
            Timestamp = (
                _Timestamp()
            )
            TimeUnit = (
                _TimeUnit()
            )

            if timestamp is None:
                timestamp = Timestamp.ISO_DATE_STRING

            if time_unit is None:
                time_unit = TimeUnit.NANOSECOND

            timestamp_nanoseconds = _time().time_ns()

            current = _datetime().datetime.fromtimestamp(
                timestamp_nanoseconds / 1_000_000_000,
                _TimeZoneManager().get_singleton().selected_time_zone,
            )

            match time_unit:
                case (
                    TimeUnit.NONE
                    | TimeUnit.SECOND
                ):
                    fraction = ""

                case TimeUnit.MILLISECOND:
                    fraction = (
                        f".{timestamp_nanoseconds // 1_000_000 % 1_000:03d}"
                    )

                case TimeUnit.MICROSECOND:
                    fraction = (
                        f".{timestamp_nanoseconds // 1_000 % 1_000_000:06d}"
                    )

                case TimeUnit.NANOSECOND:
                    fraction = (
                        f".{timestamp_nanoseconds % 1_000_000_000:09d}"
                    )

                case _:
                    fraction = ""

            if current.tzinfo is _datetime().UTC:
                suffix = "Z"
            else:
                suffix = current.strftime("%z")

                if suffix:
                    suffix = f"{suffix[:-2]}:{suffix[-2:]}"

            match timestamp:
                case Timestamp.ISO_DATE_STRING:
                    prefix = current.strftime("%Y-%m-%dT%H:%M:%S")

                case Timestamp.ISO_FILESYSTEM_STRING:
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
    _allocate = lambda: None


def TimestampManager():
    if _TimestampManager is None:
        _allocate()

    return _TimestampManager


# TimestampManager()
