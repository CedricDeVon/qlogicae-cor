from __future__ import annotations

__all__ = (
    "ScriptProcessManager",
)

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from subprocess import CompletedProcess # nosec B404

    from .script_process import (
        ScriptProcess,
    )

_shlex: Any = None
_subprocess: Any = None
_SingletonManager: Any = None
_TextEncodingManager: Any = None
_ScriptProcess: Any = None


def _handle_dynamic_imports() -> None:
    global _handle_dynamic_imports
    global _shlex
    global _subprocess
    global _SingletonManager
    global _TextEncodingManager
    global _ScriptProcess

    import shlex # nosec B404
    import subprocess # nosec B404

    from .script_process import ScriptProcess
    from .singleton_manager import SingletonManager
    from .text_encoding_manager import TextEncodingManager

    _shlex = shlex
    _subprocess = subprocess
    _SingletonManager = (
        SingletonManager
    )
    _TextEncodingManager = (
        TextEncodingManager
    )
    _ScriptProcess = (
        ScriptProcess
    )

    _handle_dynamic_imports = lambda: None


class ScriptProcessManager:
    __slots__ = (
        "_selected_script_process",
        "_valid_script_processes",
        "_text_encoding_manager",
    )

    def __init__(self) -> None:
        _handle_dynamic_imports()

        self._text_encoding_manager = (
            _SingletonManager.get_singleton(
                _TextEncodingManager
            )
        )

        self._selected_script_process: str = "shell"
        self._valid_script_processes: set[str] = {
            "shell",
            "subprocess",
        }

    @property
    def selected_script_process(self) -> str:
        return self._selected_script_process

    @selected_script_process.setter
    def selected_script_process(
        self,
        value: str,
    ) -> None:
        if value not in self._valid_script_processes:
            return

        self._selected_script_process = value

    @property
    def valid_script_processes(self) -> set[str]:
        return self._valid_script_processes

    def execute_command(
        self,
        command: str,
        script_process_type: ScriptProcess | None = None,
    ) -> CompletedProcess[str]:
        if script_process_type is None:
            script_process_type = _ScriptProcess.SUBPROCESS

        if not command:
            raise ValueError(
                "commands cannot be empty",
            )

        encoding = (
            self._text_encoding_manager.selected_encoding
        )

        value: CompletedProcess[str]

        match script_process_type:
            case _ScriptProcess.SHELL:
                value = _subprocess.run(
                    command,
                    encoding=encoding,
                    text=True, # nosec B604
                    shell=True, # nosec B604
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
