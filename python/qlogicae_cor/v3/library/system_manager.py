__all__ = (
    "SystemManager",
)

_os = None
_platform = None
_pathlib = None
_SystemManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _SystemManager

    class __SystemManager:
        __slots__ = (
            "_original_executing_console_filesystem_path",
        )

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

        @property
        def original_executing_console_filesystem_path(self):
            return self._original_executing_console_filesystem_path

        @property
        def current_executing_script_filesystem_path(self):
            return f"{_pathlib().Path(__file__).resolve()}"

        @property
        def current_executing_console_filesystem_path(self):
            return f"{_pathlib().Path.cwd().resolve()}"

        @current_executing_console_filesystem_path.setter
        def current_executing_console_filesystem_path(
            self,
            filesystem_path,
        ):
            path = (
                _pathlib().Path(filesystem_path)
                .expanduser()
                .resolve()
            )

            if not path.exists():
                raise ValueError(
                    f"directory '{path}' does not exist",
                )

            if not path.is_dir():
                raise ValueError(
                    f"'{path}' is not a directory",
                )

            _os().chdir(path)

        @property
        def operating_system_name(self):
            return _platform().system()

        @property
        def operating_system_architecture(self):
            return _platform().machine()

        def construct(self):
            global _os
            global _platform
            global _pathlib

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _os = (
                _ExternalDependencyManager().import_module(
                    path="os",
                )
            )
            _platform = (
                _ExternalDependencyManager().import_module(
                    path="platform",
                )
            )
            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
                )
            )

            self._original_executing_console_filesystem_path = (
                f"{_pathlib().Path.cwd().resolve()}"
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            self._original_executing_console_filesystem_path = (
                f"{_pathlib().Path.cwd().resolve()}"
            )

            return True


    _SystemManager = __SystemManager
    _allocate = lambda: None


def SystemManager():
    if _SystemManager is None:
        _allocate()

    return _SystemManager


# SystemManager()
