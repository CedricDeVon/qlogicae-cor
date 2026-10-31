__all__ = (
    "ScriptProcess",
)

_ScriptProcess = None


def _allocate_module():
    global _allocate_module
    global _ScriptProcess

    from enum import Enum

    class __ScriptProcess(Enum):
        SHELL = 0
        SUBPROCESS = 1
        NONE = 2

    _ScriptProcess = __ScriptProcess
    _allocate_module = lambda: None


def ScriptProcess():
    if _ScriptProcess is None:
        _allocate_module()

    return _ScriptProcess


# ScriptProcess()
