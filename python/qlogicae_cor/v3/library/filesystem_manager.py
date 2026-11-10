__all__ = (
    "FilesystemManager",
)

_shutil = None
_pathlib = None
_FileEntityFilesystemTreeSetupOptions = None
_FolderEntityFilesystemTreeSetupOptions = None
_FilesystemManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _FilesystemManager

    class __FilesystemManager:
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
            global _shutil
            global _pathlib
            global _FileEntityFilesystemTreeSetupOptions
            global _FolderEntityFilesystemTreeSetupOptions

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _shutil = (
                _ExternalDependencyManager().import_module(
                    path="shutil",
                )
            )
            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
                )
            )
            _FileEntityFilesystemTreeSetupOptions = (
                _ExternalDependencyManager().import_module(
                    path=".file_entity_filesystem_tree_setup_options",
                    package="qlogicae_cor.v3.library",
                    member="FileEntityFilesystemTreeSetupOptions",
                    is_member_callable=True,
                )
            )
            _FolderEntityFilesystemTreeSetupOptions = (
                _ExternalDependencyManager().import_module(
                    path=".folder_entity_filesystem_tree_setup_options",
                    package="qlogicae_cor.v3.library",
                    member="FolderEntityFilesystemTreeSetupOptions",
                    is_member_callable=True,
                )
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def throw_if_filesystem_path_invalid(self, value):
            if not isinstance(value, (str, _pathlib().Path)):
                raise ValueError("'value' must either be a string or Path")

            path = _pathlib().Path(value)

            if not path.exists():
                raise ValueError(
                    f"filesystem path '{path}' is invalid"
                )

            return False

        def throw_if_file_path_invalid(self, value):
            if not isinstance(value, (str, _pathlib().Path)):
                raise ValueError("'value' must either be a string or Path")

            path = _pathlib().Path(value)

            if not path.is_file():
                raise ValueError(
                    f"file path '{path}' is invalid"
                )

            return False

        def throw_if_folder_path_invalid(self, value):
            if not isinstance(value, (str, _pathlib().Path)):
                raise ValueError("'value' must either be a string or Path")

            path = _pathlib().Path(value)

            if not path.is_dir():
                raise ValueError(
                    f"folder path '{path}' is invalid"
                )

            return False

        def is_filesystem_path_valid(self, value):
            if not isinstance(value, (str, _pathlib().Path)):
                raise ValueError("'value' must either be a string or Path")

            result = _pathlib().Path(value).exists()
            return result

        def is_file_path_valid(self, value):
            if not isinstance(value, (str, _pathlib().Path)):
                raise ValueError("'value' must either be a string or Path")

            result = _pathlib().Path(value).is_file()
            return result

        def is_folder_path_valid(self, value):
            if not isinstance(value, (str, _pathlib().Path)):
                raise ValueError("'value' must either be a string or Path")

            result = _pathlib().Path(value).is_dir()
            return result

        def clean_filesystem_path(self, value):
            if not isinstance(value, (str, _pathlib().Path)):
                raise ValueError("'value' must either be a string or Path")

            directory = _pathlib().Path(value).resolve()

            protected_paths = {
                _pathlib().Path(""),
                _pathlib().Path("/"),
                _pathlib().Path.home(),
            }

            if directory in protected_paths:
                raise ValueError(
                    f"folder path '{value}' is protected"
                )

            if not directory.exists():
                return True

            if not directory.is_dir():
                raise ValueError(
                    f"file path '{value}' is not a folder"
                )

            for item in directory.iterdir():
                if item.is_file() or item.is_symlink():
                    item.unlink()

                elif item.is_dir():
                    _shutil().rmtree(item)

            return True

        def copy_filesystem_path(
            self,
            first_path,
            second_path,
        ):
            if not isinstance(first_path, (str, _pathlib().Path)):
                raise ValueError("'first_path' must either be a string or Path")

            if not isinstance(second_path, (str, _pathlib().Path)):
                raise ValueError("'second_path' must either be a string or Path")

            fs_first_path = _pathlib().Path(first_path)
            fs_second_path = _pathlib().Path(second_path)

            if fs_first_path.is_dir():
                _shutil().copytree(
                    fs_first_path,
                    fs_second_path,
                    dirs_exist_ok=True,
                )

            elif fs_first_path.is_file():
                fs_second_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                _shutil().copy2(
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
            if not isinstance(first_path, (str, _pathlib().Path)):
                raise ValueError("'first_path' must either be a string or Path")

            if not isinstance(second_path, (str, _pathlib().Path)):
                raise ValueError("'second_path' must either be a string or Path")

            source = _pathlib().Path(first_path)
            destination = _pathlib().Path(second_path)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            _shutil().move(
                str(source),
                str(destination),
            )

            return True

        def setup_filesystem_tree(
            self,
            parent_path,
            options,
        ):
            if not isinstance(parent_path, (str, _pathlib().Path)):
                raise ValueError("'parent_path' must either be a string or Path")

            if not isinstance(options, (_FolderEntityFilesystemTreeSetupOptions())):
                raise ValueError(
                    "'options' must be a 'FolderEntityFilesystemTreeSetupOptions'"
                )

            path = _pathlib().Path(parent_path)

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
                    _FolderEntityFilesystemTreeSetupOptions(),
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
                    _FileEntityFilesystemTreeSetupOptions(),
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
            if not isinstance(source, (str, _pathlib().Path)):
                raise ValueError("'source' must either be a string or Path")

            if not isinstance(destination, (str, _pathlib().Path)):
                raise ValueError("'destination' must either be a string or Path")

            _pathlib().Path(source).rename(destination)

            return True

        def setup_filesystem_tree_path(self, directory):
            if not isinstance(directory, (str, _pathlib().Path)):
                raise ValueError("'directory' must either be a string or Path")

            _pathlib().Path(directory).mkdir(
                parents=True,
                exist_ok=True,
            )

            return True

    _FilesystemManager = __FilesystemManager
    _allocate = lambda: None


def FilesystemManager():
    if _FilesystemManager is None:
        _allocate()

    return _FilesystemManager


# FilesystemManager()
