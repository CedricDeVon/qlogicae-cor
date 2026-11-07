__all__ = (
    "LogOptions",
)

_LogOptions = None

def _allocate():
    global _allocate
    global _LogOptions

    from dataclasses import dataclass

    @dataclass(frozen=True, slots=True)
    class __LogOptions:
        is_enabled: bool = True
        is_verbose_enabled: bool = True
        log_level: int = 10
        stack_level: int = 3
        target_filesystem_paths: tuple[str] = tuple()

    _LogOptions = __LogOptions
    _allocate = lambda: None


def LogOptions():
    if _LogOptions is None:
        _allocate()

    return _LogOptions


# LogOptions()
