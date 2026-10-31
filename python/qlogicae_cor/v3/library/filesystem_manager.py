__all__ = (
    "FilesystemManager",
)

_shutil = None
_Path = None
_FileEntityFilesystemTreeSetupOptions = None
_FolderEntityFilesystemTreeSetupOptions = None
_FilesystemManager = None


def _allocate_module():
    global _allocate_module
    global _shutil
    global _Path
    global _FileEntityFilesystemTreeSetupOptions
    global _FolderEntityFilesystemTreeSetupOptions
    global _FilesystemManager

    import shutil
    from pathlib import Path

    from .file_entity_filesystem_tree_setup_options import (
        FileEntityFilesystemTreeSetupOptions,
    )
    from .folder_entity_filesystem_tree_setup_options import (
        FolderEntityFilesystemTreeSetupOptions,
    )

    _shutil = shutil
    _Path = Path
    _FileEntityFilesystemTreeSetupOptions = FileEntityFilesystemTreeSetupOptions()
    _FolderEntityFilesystemTreeSetupOptions = FolderEntityFilesystemTreeSetupOptions()

    class __FilesystemManager:
        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def throw_if_filesystem_path_invalid(self, value):
            path = _Path(value)

            if not path.exists():
                raise ValueError(
                    f"filesystem path '{path}' is invalid"
                )

            return False

        def throw_if_file_path_invalid(self, value):
            path = _Path(value)

            if not path.is_file():
                raise ValueError(
                    f"file path '{path}' is invalid"
                )

            return False

        def throw_if_folder_path_invalid(self, value):
            path = _Path(value)

            if not path.is_dir():
                raise ValueError(
                    f"folder path '{path}' is invalid"
                )

            return False

        def is_filesystem_path_valid(self, value):
            result = _Path(value).exists()
            return result

        def is_file_path_valid(self, value):
            result = _Path(value).is_file()
            return result

        def is_folder_path_valid(self, value):
            result = _Path(value).is_dir()
            return result

        def clean_filesystem_path(self, path):
            directory = _Path(path).resolve()

            protected_paths = {
                _Path(""),
                _Path("/"),
                _Path.home(),
            }

            if directory in protected_paths:
                raise ValueError(
                    f"folder path '{path}' is protected"
                )

            if not directory.exists():
                return True

            if not directory.is_dir():
                raise ValueError(
                    f"file path '{path}' is not a folder"
                )

            for item in directory.iterdir():
                if item.is_file() or item.is_symlink():
                    item.unlink()

                elif item.is_dir():
                    _shutil.rmtree(item)

            return True

        def copy_filesystem_path(
            self,
            first_path,
            second_path,
        ):
            fs_first_path = _Path(first_path)
            fs_second_path = _Path(second_path)

            if fs_first_path.is_dir():
                _shutil.copytree(
                    fs_first_path,
                    fs_second_path,
                    dirs_exist_ok=True,
                )

            elif fs_first_path.is_file():
                fs_second_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                _shutil.copy2(
                    fs_first_path,
                    fs_second_path,
                )

            else:
                return False

            return True

        def move_filesystem_path(
            self,
            first_path,
            second_path,
        ):
            source = _Path(first_path)
            destination = _Path(second_path)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            _shutil.move(
                str(source),
                str(destination),
            )

            return True

        def setup_filesystem_tree(
            self,
            parent_path,
            options,
        ):
            path = _Path(parent_path)

            if not path.exists():
                raise ValueError(
                    f"filesystem path '{path}' is invalid"
                )

            path.mkdir(
                parents=True,
                exist_ok=True,
            )

            for entity in options.entities or []:
                entity_path = path / entity.name

                if isinstance(
                    entity,
                    _FolderEntityFilesystemTreeSetupOptions,
                ):
                    entity_path.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    self.setup_filesystem_tree(
                        entity_path,
                        entity,
                    )

                elif isinstance(
                    entity,
                    _FileEntityFilesystemTreeSetupOptions,
                ):
                    if not entity_path.exists():
                        entity_path.write_text(
                            entity.content,
                            encoding=entity.encoding,
                        )

        def rename_filesystem_entity(
            self,
            source,
            destination,
        ):
            _Path(source).rename(destination)

            return True

        def setup_filesystem_tree_path(self, directory):
            _Path(directory).mkdir(
                parents=True,
                exist_ok=True,
            )

            return True

    _FilesystemManager = __FilesystemManager
    _allocate_module = lambda: None


def FilesystemManager():
    if _FilesystemManager is None:
        _allocate_module()

    return _FilesystemManager


# FilesystemManager()
