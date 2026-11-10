__all__ = (
    "FilesystemCompressionManager",
)

_zipfile = None
_pathlib = None
_FilesystemCompressionManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _FilesystemCompressionManager

    class __FilesystemCompressionManager:
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
            global _zipfile
            global _pathlib

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _zipfile = (
                _ExternalDependencyManager().import_module(
                    path="zipfile",
                )
            )
            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
                )
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def get_zip_format_compression(
            self,
            value,
        ):
            if not isinstance(value, (str)):
                raise ValueError("'value' must be a string")

            match value.lower():
                case "store" | "stored" | "none":
                    result = _zipfile().ZIP_STORED

                case "deflate" | "deflated":
                    result = _zipfile().ZIP_DEFLATED

                case "bz2" | "bzip2":
                    result = _zipfile().ZIP_BZIP2

                case "lzma" | "xz":
                    result = _zipfile().ZIP_LZMA

                case _:
                    result = _zipfile().ZIP_DEFLATED

            return result

        def zip_extract(
            self,
            archive_path,
            destination_path,
            overwrite=False,
        ):
            if not isinstance(archive_path, (str, _pathlib().Path)):
                raise ValueError("'archive_path' must either be a string or Path")

            if not isinstance(destination_path, (str, _pathlib().Path)):
                raise ValueError("'destination_path' must either be a string or Path")

            if not isinstance(overwrite, (bool)):
                raise ValueError("'overwrite' must be a boolean")

            fs_archive_path = _pathlib().Path(archive_path)
            fs_destination_path = _pathlib().Path(
                destination_path,
            ).resolve()

            fs_destination_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            with _zipfile().ZipFile(
                fs_archive_path,
                "r",
            ) as archive:
                for member in archive.infolist():
                    target = (
                        fs_destination_path
                        / member.filename
                    ).resolve()

                    if (
                        fs_destination_path not in target.parents
                        and target != fs_destination_path
                    ):
                        raise ValueError(
                            f"unsafe archive filesystem path "
                            f"'{member.filename}'"
                        )

                    if not overwrite and target.exists():
                        continue

                    archive.extract(
                        member,
                        fs_destination_path,
                    )

            return True

    _FilesystemCompressionManager = __FilesystemCompressionManager
    _allocate = lambda: None


def FilesystemCompressionManager():
    if _FilesystemCompressionManager is None:
        _allocate()

    return _FilesystemCompressionManager


# FilesystemCompressionManager()
