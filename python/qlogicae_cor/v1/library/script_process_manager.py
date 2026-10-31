from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from subprocess import CompletedProcess # nosec B404

    from qlogicae_cor.v1.library.script_process import (
        ScriptProcess,
    )

_shlex: Any = None
_subprocess: Any = None
_singleton_manager: Any = None
_text_encoding_manager: Any = None
_script_process: Any = None


def _handle_dynamic_imports() -> None:
    global _handle_dynamic_imports
    global _shlex
    global _subprocess
    global _singleton_manager
    global _text_encoding_manager
    global _script_process

    import shlex # nosec B404
    import subprocess # nosec B404

    import qlogicae_cor.v1.library.script_process
    import qlogicae_cor.v1.library.singleton_manager
    import qlogicae_cor.v1.library.text_encoding_manager

    _shlex = shlex
    _subprocess = subprocess
    _singleton_manager = (
        qlogicae_cor.v1.library.singleton_manager.SingletonManager
    )
    _text_encoding_manager = (
        qlogicae_cor.v1.library.text_encoding_manager.TextEncodingManager
    )
    _script_process = (
        qlogicae_cor.v1.library.script_process.ScriptProcess
    )

    _handle_dynamic_imports = lambda: None


class ScriptProcessManager:
    __slots__ = (
        "_selected_script_process",
        "_valid_script_processes",
    )

    def __init__(self) -> None:
        _handle_dynamic_imports()

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
            script_process_type = _script_process.SUBPROCESS

        if not command:
            raise ValueError(
                "commands cannot be empty",
            )

        encoding = (
            _singleton_manager
            .get_singleton(
                _text_encoding_manager,
            )
            .selected_encoding
        )

        value: CompletedProcess[str]

        match script_process_type:
            case _script_process.SHELL:
                value = _subprocess.run(
                    command,
                    encoding=encoding,
                    text=True, # nosec B604
                    shell=True, # nosec B604
                )

            case _script_process.SUBPROCESS:
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
