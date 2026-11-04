__all__ = (
    "ScriptProcess",
)

_ScriptProcess = None


def _allocate():
    global _allocate
    global _ScriptProcess

    from enum import Enum

    class __ScriptProcess(Enum):
        SHELL = 0
        SUBPROCESS = 1
        NONE = 2

    _ScriptProcess = __ScriptProcess
    _allocate = lambda: None


def ScriptProcess():
    if _ScriptProcess is None:
        _allocate()

    return _ScriptProcess


# ScriptProcess()
