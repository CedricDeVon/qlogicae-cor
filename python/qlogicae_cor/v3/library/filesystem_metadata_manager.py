__all__ = (
    "FilesystemMetadataManager",
)

_Path = None
_FilesystemMetadata = None
_FilesystemMetadataManager = None


def _allocate_module():
    global _allocate_module
    global _FilesystemMetadataManager

    class __FilesystemMetadataManager:
        _singleton = None

        def __init__(self):
            self.construct()

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _Path
            global _FilesystemMetadata

            from pathlib import Path

            from .filesystem_metadata import FilesystemMetadata

            _Path = Path
            _FilesystemMetadata = FilesystemMetadata

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            return True

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
