__all__ = (
    "FilesystemMetadataManager",
)

_Path = None
_FilesystemMetadata = None
_FilesystemMetadataManager = None


def _allocate_module():
    global _allocate_module
    global _Path
    global _FilesystemMetadata
    global _FilesystemMetadataManager

    from pathlib import Path

    from .filesystem_metadata import FilesystemMetadata

    _Path = Path
    _FilesystemMetadata = FilesystemMetadata

    class __FilesystemMetadataManager:
        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def read_metadata(
            self,
            filesystem_path,
        ):
            stat = _Path(filesystem_path).stat()

            return _FilesystemMetadata(
                mode=stat.st_mode,
                inode=stat.st_ino,
                device=stat.st_dev,
                hard_links=stat.st_nlink,
                uid=stat.st_uid,
                gid=stat.st_gid,
                size=stat.st_size,
                access_time=stat.st_atime,
                modification_time=stat.st_mtime,
                status_change_time=stat.st_ctime,
            )

    _FilesystemMetadataManager = __FilesystemMetadataManager
    _allocate_module = lambda: None


def FilesystemMetadataManager():
    if _FilesystemMetadataManager is None:
        _allocate_module()

    return _FilesystemMetadataManager


# FilesystemMetadataManager()
