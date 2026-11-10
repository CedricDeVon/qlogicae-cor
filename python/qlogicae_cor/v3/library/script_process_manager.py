__all__ = (
    "ScriptProcessManager",
)

_shlex = None
_subprocess = None
_TextEncodingManager = None
_ScriptProcess = None
_ScriptProcessManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _ScriptProcessManager

    class __ScriptProcessManager:
        __slots__ = (
            "_selected_script_process",
            "_valid_script_processes",
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

        def construct(self):
            global _shlex
            global _subprocess
            global _TextEncodingManager
            global _ScriptProcess

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )
            _shlex = (
                _ExternalDependencyManager().import_module(
                    path="shlex",
                )
            )
            _subprocess = (
                _ExternalDependencyManager().import_module(
                    path="subprocess",
                )
            )
            _TextEncodingManager = (
                _ExternalDependencyManager().import_module(
                    path=".text_encoding_manager",
                    package="qlogicae_cor.v3.library",
                    member="TextEncodingManager",
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

            self._selected_script_process = "subprocess"
            self._valid_script_processes = {
                "shell",
                "subprocess",
            }

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def execute_command(
            self,
            command,
            script_process_type=None,
        ):
            ScriptProcess = (
                _ScriptProcess()
            )

            if script_process_type is None:
                script_process_type = ScriptProcess.SUBPROCESS

            if not command:
                raise ValueError(
                    "commands cannot be empty",
                )

            encoding = (
                _TextEncodingManager()
                    .get_singleton()
                    .selected_encoding
            )

            match script_process_type:
                case ScriptProcess.SHELL:
                    value = _subprocess().run(  # nosec B604
                        command,
                        encoding=encoding,
                        text=True,
                        shell=True,
                    )

                case ScriptProcess.SUBPROCESS:
                    value = _subprocess().run(
                        _shlex().split(command),
                        encoding=encoding,
                        text=True,
                    )

                case _:
                    raise ValueError(
                        "unsupported script process value",
                    )

            return value

    _ScriptProcessManager = __ScriptProcessManager
    _allocate = lambda: None


def ScriptProcessManager():
    if _ScriptProcessManager is None:
        _allocate()

    return _ScriptProcessManager


# ScriptProcessManager()
