__all__ = (
    "FileEntityFilesystemTreeSetupOptions",
)

_FileEntityFilesystemTreeSetupOptions = None


def _allocate_module():
    global _allocate_module
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
    _allocate_module = lambda: None


def FileEntityFilesystemTreeSetupOptions():
    if _FileEntityFilesystemTreeSetupOptions is None:
        _allocate_module()

    return _FileEntityFilesystemTreeSetupOptions


# FileEntityFilesystemTreeSetupOptions()
