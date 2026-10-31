__all__ = (
    "FolderEntityFilesystemTreeSetupOptions",
)

_FolderEntityFilesystemTreeSetupOptions = None


def _allocate_module():
    global _allocate_module
    global _FolderEntityFilesystemTreeSetupOptions

    from dataclasses import dataclass, field
    from typing import Any

    @dataclass(frozen=True, slots=True)
    class __FolderEntityFilesystemTreeSetupOptions:
        name: str = "folder"
        entities: list[Any] = field(default_factory=list)

    _FolderEntityFilesystemTreeSetupOptions = (
        __FolderEntityFilesystemTreeSetupOptions
    )
    _allocate_module = lambda: None


def FolderEntityFilesystemTreeSetupOptions():
    if _FolderEntityFilesystemTreeSetupOptions is None:
        _allocate_module()

    return _FolderEntityFilesystemTreeSetupOptions


# FolderEntityFilesystemTreeSetupOptions()
