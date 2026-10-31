__all__ = (
    "LogOptions",
)

_LogOptions = None

def _allocate_module():
    global _allocate_module
    global _LogOptions

    from dataclasses import dataclass

    @dataclass(frozen=True, slots=True)
    class __LogOptions:
        is_enabled: bool = True
        is_verbose_enabled: bool = True
        log_level: int = 10
        stack_level: int = 3

    _LogOptions = __LogOptions
    _allocate_module = lambda: None


def LogOptions():
    if _LogOptions is None:
        _allocate_module()

    return _LogOptions


# LogOptions()
