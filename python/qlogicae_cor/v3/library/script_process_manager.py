__all__ = (
    "ScriptProcessManager",
)

_shlex = None
_subprocess = None
_PythonRuntimeUtilityManager = None
_TextEncodingManager = None
_ScriptProcess = None
_ScriptProcessManager = None


def _allocate_module():
    global _allocate_module
    global _shlex
    global _subprocess
    global _PythonRuntimeUtilityManager
    global _TextEncodingManager
    global _ScriptProcess
    global _ScriptProcessManager

    import shlex  # nosec B404
    import subprocess  # nosec B404

    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .script_process import ScriptProcess
    from .text_encoding_manager import TextEncodingManager

    _shlex = shlex
    _subprocess = subprocess
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _TextEncodingManager = TextEncodingManager().get_singleton
    _ScriptProcess = ScriptProcess()

    class __ScriptProcessManager:
        __slots__ = (
            "_selected_script_process",
            "_valid_script_processes",
        )

        _singleton = None

        def __init__(self):
            if (
                _PythonRuntimeUtilityManager
                .is_allocated_during_object_construction
            ):
                _TextEncodingManager()

            self._selected_script_process = "subprocess"
            self._valid_script_processes = {
                "shell",
                "subprocess",
            }

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def selected_script_process(self):
            return self._selected_script_process

        @selected_script_process.setter
        def selected_script_process(self, value):
            if value not in self._valid_script_processes:
                return

            self._selected_script_process = value

        @property
        def valid_script_processes(self):
            return self._valid_script_processes

        def execute_command(
            self,
            command,
            script_process_type=None,
        ):
            if script_process_type is None:
                script_process_type = _ScriptProcess.SUBPROCESS

            if not command:
                raise ValueError(
                    "commands cannot be empty",
                )

            encoding = (
                _TextEncodingManager().selected_encoding
            )

            match script_process_type:
                case _ScriptProcess.SHELL:
                    value = _subprocess.run(  # nosec B604
                        command,
                        encoding=encoding,
                        text=True,
                        shell=True,
                    )

                case _ScriptProcess.SUBPROCESS:
                    value = _subprocess.run(
                        _shlex.split(command),
                        encoding=encoding,
                        text=True,
                    )

                case _:
                    raise ValueError(
                        "unsupported script process value",
                    )

            return value

    _ScriptProcessManager = __ScriptProcessManager
    _allocate_module = lambda: None


def ScriptProcessManager():
    if _ScriptProcessManager is None:
        _allocate_module()

    return _ScriptProcessManager


# ScriptProcessManager()
