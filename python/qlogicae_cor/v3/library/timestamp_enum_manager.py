__all__ = (
    "TimestampEnumManager",
)

_EnumConversionValue = None
_Timestamp = None
_TimestampEnumManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _TimestampEnumManager

    class __TimestampEnumManager:
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
            global _Timestamp
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
            _Timestamp = (
                _ExternalDependencyManager().import_module(
                    path=".timestamp",
                    package="qlogicae_cor.v3.library",
                    member="Timestamp",
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
            Timestamp = (
                _Timestamp()
            )

            if output_type is None:
                output_type = EnumConversionValue.STRING

            match output_type:
                case EnumConversionValue.STRING:
                    match input_type:
                        case Timestamp.ISO_DATE_STRING:
                            return "iso_date_string"

                        case Timestamp.ISO_FILESYSTEM_STRING:
                            return "iso_filesystem_string"

                        case _:
                            return "iso_date_string"

                case EnumConversionValue.ENUM:
                    match input_type.lower():
                        case "local":
                            return Timestamp.ISO_DATE_STRING

                        case "iso_filesystem_string":
                            return Timestamp.ISO_FILESYSTEM_STRING

                        case _:
                            return Timestamp.NONE

                case _:
                    return EnumConversionValue.NONE

    _TimestampEnumManager = __TimestampEnumManager
    _allocate = lambda: None


def TimestampEnumManager():
    if _TimestampEnumManager is None:
        _allocate()

    return _TimestampEnumManager


# TimestampEnumManager()
