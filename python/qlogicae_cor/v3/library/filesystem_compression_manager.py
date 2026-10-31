__all__ = (
    "FilesystemCompressionManager",
)

_zipfile = None
_Path = None
_FilesystemCompressionManager = None


def _allocate_module():
    global _allocate_module
    global _zipfile
    global _Path
    global _FilesystemCompressionManager

    import zipfile
    from pathlib import Path

    _zipfile = zipfile
    _Path = Path

    class __FilesystemCompressionManager:
        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def get_zip_format_compression(
            self,
            value,
        ):
            match value.lower():
                case "store" | "stored" | "none":
                    result = _zipfile.ZIP_STORED

                case "deflate" | "deflated":
                    result = _zipfile.ZIP_DEFLATED

                case "bz2" | "bzip2":
                    result = _zipfile.ZIP_BZIP2

                case "lzma" | "xz":
                    result = _zipfile.ZIP_LZMA

                case _:
                    result = _zipfile.ZIP_DEFLATED

            return result

        def zip_extract(
            self,
            archive_path,
            destination_path,
            overwrite=False,
        ):
            fs_archive_path = _Path(archive_path)
            fs_destination_path = _Path(
                destination_path,
            ).resolve()

            fs_destination_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            with _zipfile.ZipFile(
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
    _allocate_module = lambda: None


def FilesystemCompressionManager():
    if _FilesystemCompressionManager is None:
        _allocate_module()

    return _FilesystemCompressionManager


# FilesystemCompressionManager()
