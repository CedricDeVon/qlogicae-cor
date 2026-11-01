__all__ = (
    "PythonModuleManager",
)

_sys = None
_pathlib = None
_importlib_util = None
_PythonModuleManager = None
_PythonRuntimeUtilityManager = None


def _allocate_module():
    global _allocate_module

    global _sys
    global _pathlib
    global _importlib_util
    global _PythonModuleManager
    global _PythonRuntimeUtilityManager


    import importlib.util
    import pathlib
    import sys

    from .python_runtime_utility_manager import PythonRuntimeUtilityManager

    _sys = sys
    _pathlib = pathlib
    _importlib_util = importlib.util
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()

    class __PythonModuleManager:
        _singleton = None

        def __init__(self):
            pass

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def read_import_modules(
            self,
            **kwargs,
        ):
            if not kwargs:
                return tuple()

            target_filesystem_paths = kwargs.get(
                "target_filesystem_paths",
                (),
            ) or ()

            if isinstance(target_filesystem_paths, (str, _pathlib.Path)):
                target_filesystem_paths = (target_filesystem_paths,)

            if not target_filesystem_paths:
                return tuple()

            is_recursive = kwargs.get("is_recursive", True)

            folder_paths = tuple(
                dict.fromkeys(
                    (
                        _pathlib.Path.cwd() / path
                    ).resolve()
                    for path in target_filesystem_paths
                )
            )
            if not folder_paths:
                return tuple()

            excluded_paths = {
                (
                    _pathlib.Path.cwd() / path
                ).resolve()
                for path in (
                    kwargs.get("excluded_filesystem_paths", ()) or ()
                )
            }

            modules = []
            imported_file_paths = set()

            for folder_path in folder_paths:
                if not folder_path.is_dir():
                    continue

                file_paths = (
                    folder_path.rglob("*.py")
                    if is_recursive
                    else folder_path.glob("*.py")
                )

                for file_path in sorted(file_paths):
                    resolved_file_path = file_path.resolve()

                    if resolved_file_path in imported_file_paths:
                        continue

                    if any(
                        resolved_file_path == excluded_path
                        or excluded_path in resolved_file_path.parents
                        for excluded_path in excluded_paths
                    ):
                        continue

                    imported_file_paths.add(resolved_file_path)

                    relative_path = file_path.relative_to(folder_path)

                    if file_path.name == "__init__.py":
                        module_parts = relative_path.parent.parts
                    else:
                        module_parts = (
                            *relative_path.parent.parts,
                            file_path.stem,
                        )

                    if not module_parts:
                        continue

                    module_name = ".".join(module_parts)

                    spec = _importlib_util.spec_from_file_location(
                        module_name,
                        file_path,
                    )

                    if spec is None or spec.loader is None:
                        raise ImportError(
                            f"Cannot load module from {file_path}"
                        )

                    module = _importlib_util.module_from_spec(spec)

                    _sys.modules[module_name] = module

                    try:
                        spec.loader.exec_module(module)

                    except BaseException:
                        _sys.modules.pop(module_name, None)
                        raise

                    modules.append(module)

            return tuple(modules)


    _PythonModuleManager = __PythonModuleManager
    _allocate_module = lambda: None


def PythonModuleManager():
    if _PythonModuleManager is None:
        _allocate_module()

    return _PythonModuleManager


# PythonModuleManager()
