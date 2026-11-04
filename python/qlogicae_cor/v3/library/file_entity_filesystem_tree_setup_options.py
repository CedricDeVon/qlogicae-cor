__all__ = (
    "FileEntityFilesystemTreeSetupOptions",
)

_FileEntityFilesystemTreeSetupOptions = None


def _allocate():
    global _allocate
    global _FileEntityFilesystemTreeSetupOptions

    from dataclasses import dataclass

    @dataclass(frozen=True, slots=True)
    class __FileEntityFilesystemTreeSetupOptions:
        content: str = "data"
        name: str = "file"
        encoding: str = "utf-8"
        is_modifiable: bool = False

    _FileEntityFilesystemTreeSetupOptions = (
        __FileEntityFilesystemTreeSetupOptions
    )
    _allocate = lambda: None


def FileEntityFilesystemTreeSetupOptions():
    if _FileEntityFilesystemTreeSetupOptions is None:
        _allocate()

    return _FileEntityFilesystemTreeSetupOptions


# FileEntityFilesystemTreeSetupOptions()
