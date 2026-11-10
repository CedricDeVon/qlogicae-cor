__all__ = (
    "EnumConversionValueEnumManager",
)

_EnumConversionValue = None
_EnumConversionValueEnumManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _EnumConversionValueEnumManager

    class __EnumConversionValueEnumManager:
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
            global _ExternalDependencyManager
            global _EnumConversionValue

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

            if output_type is None:
                output_type = EnumConversionValue.STRING

            match output_type:
                case EnumConversionValue.STRING:
                    match input_type:
                        case EnumConversionValue.STRING:
                            return "string"

                        case EnumConversionValue.ENUM:
                            return "enum"

                        case EnumConversionValue.CUSTOM:
                            return "custom"

                        case _:
                            return "none"

                case EnumConversionValue.ENUM:
                    match str(input_type).lower():
                        case "string":
                            return EnumConversionValue.STRING

                        case "none":
                            return EnumConversionValue.ENUM

                        case "custom":
                            return EnumConversionValue.CUSTOM

                        case _:
                            return EnumConversionValue.NONE

                case _:
                    return EnumConversionValue.NONE

    _EnumConversionValueEnumManager = __EnumConversionValueEnumManager
    _allocate = lambda: None


def EnumConversionValueEnumManager():
    if _EnumConversionValueEnumManager is None:
        _allocate()

    return _EnumConversionValueEnumManager


# EnumConversionValueEnumManager()
