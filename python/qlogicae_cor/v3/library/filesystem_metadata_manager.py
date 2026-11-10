__all__ = (
    "FilesystemMetadataManager",
)

_pathlib = None
_FilesystemMetadata = None
_FilesystemMetadataManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _FilesystemMetadataManager

    class __FilesystemMetadataManager:
        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _ExternalDependencyManager
            global _pathlib
            global _FilesystemMetadata

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
                )
            )
            _FilesystemMetadata = (
                _ExternalDependencyManager().import_module(
                    path=".filesystem_metadata",
                    package="qlogicae_cor.v3.library",
                    member="FilesystemMetadata",
                    is_member_callable=True
                )
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def read_metadata(
            self,
            filesystem_path,
        ):
            if not isinstance(filesystem_path, (str, _pathlib().Path)):
                raise ValueError("'filesystem_path' must either be a string or Path")

            stat = _pathlib().Path(filesystem_path).stat()

            return _FilesystemMetadata()(
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
    _allocate = lambda: None


def FilesystemMetadataManager():
    if _FilesystemMetadataManager is None:
        _allocate()

    return _FilesystemMetadataManager


# FilesystemMetadataManager()
