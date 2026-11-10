__all__ = (
    "ScriptProcessEnumManager",
)

_EnumConversionValue = None
_ScriptProcess = None
_ScriptProcessEnumManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _ScriptProcessEnumManager

    class __ScriptProcessEnumManager:
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
            global _ScriptProcess

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _EnumConversionValue = (
                _ExternalDependencyManager().import_module(
                    path=".enum_conversion_value",
                    package="qlogicae_cor.v3.library",
                    member="EnumConversionValueScriptProcess",
                    is_member_callable=True,
                )
            )
            _ScriptProcess = (
                _ExternalDependencyManager().import_module(
                    path=".script_process",
                    package="qlogicae_cor.v3.library",
                    member="ScriptProcess",
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
            ScriptProcess = (
                _ScriptProcess()
            )

            if output_type is None:
                output_type = EnumConversionValue.STRING

            match output_type:
                case EnumConversionValue.STRING:
                    match input_type:
                        case ScriptProcess.SHELL:
                            return "shell"

                        case ScriptProcess.SUBPROCESS:
                            return "subprocess"

                        case _:
                            return "none"

                case EnumConversionValue.ENUM:
                    match str(input_type).lower():
                        case "shell":
                            return ScriptProcess.SHELL

                        case "subprocess":
                            return ScriptProcess.SUBPROCESS

                        case _:
                            return ScriptProcess.SUBPROCESS

                case _:
                    return EnumConversionValue.NONE

    _ScriptProcessEnumManager = __ScriptProcessEnumManager
    _allocate = lambda: None


def ScriptProcessEnumManager():
    if _ScriptProcessEnumManager is None:
        _allocate()

    return _ScriptProcessEnumManager


# ScriptProcessEnumManager()
