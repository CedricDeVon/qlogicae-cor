__all__ = (
    "FilesystemMetadata",
)

_FilesystemMetadata = None


def _allocate_module():
    global _allocate_module
    global _FilesystemMetadata

    from dataclasses import dataclass

    @dataclass(frozen=True, slots=True)
    class __FilesystemMetadata:
        mode: int
        inode: int
        device: int
        hard_links: int
        uid: int
        gid: int
        size: int
        access_time: float
        modification_time: float
        status_change_time: float

    _FilesystemMetadata = __FilesystemMetadata
    _allocate_module = lambda: None


def FilesystemMetadata():
    if _FilesystemMetadata is None:
        _allocate_module()

    return _FilesystemMetadata


# FilesystemMetadata()
