__all__ = (
    "SystemManager",
)

_os = None
_platform = None
_path = None
_SystemManager = None


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
            return f"{_path(__file__).resolve()}"

        @property
        def current_executing_console_filesystem_path(self):
            return f"{_path.cwd().resolve()}"

        @current_executing_console_filesystem_path.setter
        def current_executing_console_filesystem_path(
            self,
            filesystem_path,
        ):
            path = (
                _path(filesystem_path)
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

            _os.chdir(path)

        @property
        def operating_system_name(self):
            return _platform.system()

        @property
        def operating_system_architecture(self):
            return _platform.machine()

        def construct(self):
            global _os
            global _platform
            global _path

            import os
            import pathlib
            import platform

            _os = os
            _platform = platform
            _path = pathlib.Path

            self._original_executing_console_filesystem_path = (
                f"{_path.cwd().resolve()}"
            )

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(self):
            self._original_executing_console_filesystem_path = (
                f"{_path.cwd().resolve()}"
            )

            return True


    _SystemManager = __SystemManager
    _allocate = lambda: None


def SystemManager():
    if _SystemManager is None:
        _allocate()

    return _SystemManager


# SystemManager()
