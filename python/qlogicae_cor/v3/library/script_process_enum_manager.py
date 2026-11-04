__all__ = (
    "ScriptProcessEnumManager",
)

_EnumConversionValue = None
_ScriptProcess = None
_ScriptProcessEnumManager = None


def _allocate():
    global _allocate
    global _ScriptProcessEnumManager

    class __ScriptProcessEnumManager:
        _singleton = None

        def __init__(self):
            self.construct()

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _EnumConversionValue
            global _ScriptProcess

            from .enum_conversion_value import EnumConversionValue
            from .script_process import ScriptProcess

            _EnumConversionValue = EnumConversionValue()
            _ScriptProcess = ScriptProcess()

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True

        def convert_value(
            self,
            input_type,
            output_type=None,
        ):
            if output_type is None:
                output_type = _EnumConversionValue.STRING

            match output_type:
                case _EnumConversionValue.STRING:
                    match input_type:
                        case _ScriptProcess.SHELL:
                            return "shell"

                        case _ScriptProcess.SUBPROCESS:
                            return "subprocess"

                        case _:
                            return "none"

                case _EnumConversionValue.ENUM:
                    match str(input_type).lower():
                        case "shell":
                            return _ScriptProcess.SHELL

                        case "subprocess":
                            return _ScriptProcess.SUBPROCESS

                        case _:
                            return _ScriptProcess.SUBPROCESS

                case _:
                    return _EnumConversionValue.NONE

    _ScriptProcessEnumManager = __ScriptProcessEnumManager
    _allocate = lambda: None


def ScriptProcessEnumManager():
    if _ScriptProcessEnumManager is None:
        _allocate()

    return _ScriptProcessEnumManager


# ScriptProcessEnumManager()
