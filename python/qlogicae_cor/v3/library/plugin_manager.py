__all__ = (
    "PluginManager",
)

_sys = None
_pathlib = None
_importlib_util = None
_PluginManager = None
_ObjectMergeManager = None
_PythonModuleManager = None
_PythonRuntimeUtilityManager = None


def _allocate_module():
    global _allocate_module

    global _sys
    global _pathlib
    global _importlib_util
    global _PluginManager
    global _ObjectMergeManager
    global _PythonModuleManager
    global _PythonRuntimeUtilityManager

    import importlib.util
    import pathlib
    import sys

    from .object_merge_manager import ObjectMergeManager
    from .python_module_manager import PythonModuleManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager

    _sys = sys
    _pathlib = pathlib
    _importlib_util = importlib.util
    _ObjectMergeManager = ObjectMergeManager().get_singleton
    _PythonModuleManager = PythonModuleManager().get_singleton
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()


    class __PluginManager:
        _singleton = None

        def __init__(self):
            if (
                _PythonRuntimeUtilityManager
                    .is_allocated_during_object_construction
            ):
                _ObjectMergeManager()
                _PythonModuleManager()

            self._module_exports = {}

        @property
        def module_exports(self):
            return self._module_exports

        @module_exports.setter
        def module_exports(self, value):
            self._module_exports = value

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def setup(
            self,
            **kwargs,
        ):
            if not kwargs:
                return False

            options = (
                kwargs.get(
                    "options",
                    {}
                ) or {}
            )
            if not options:
                return False

            imported_modules = (
                self.setup_imported_modules(
                    options
                )
            )
            raw_module_exports = (
                self.setup_raw_module_exports(
                    imported_modules
                )
            )
            module_exports = (
                self.setup_merged_raw_module_exports(
                    raw_module_exports
                )
            )
            self._module_exports = (
                module_exports
            )

            return True

        def setup_imported_modules(
            self,
            options,
        ):
            if not options:
                return {}

            imported_modules = (
                _PythonModuleManager()
                    .read_import_modules(
                        **options
                    )
            )

            return (
                imported_modules
            )

        def setup_raw_module_exports(
            self,
            imported_modules
        ):
            if not imported_modules:
                return {}

            raw_module_exports = (
                self.read_plugin_module_export(
                    imported_module
                ) for imported_module in imported_modules
            )

            return (
                raw_module_exports
            )

        def setup_merged_raw_module_exports(
            self,
            raw_module_exports
        ):
            if not raw_module_exports:
                return {}

            object_merge_manager = (
                _ObjectMergeManager()
            )
            module_exports = {}
            for raw_module_export in raw_module_exports:
                if not raw_module_export:
                    continue

                module_exports = (
                    object_merge_manager.deep_merge(
                        module_exports,
                        raw_module_export
                    )
                )

            return (
                module_exports
            )


        def read_plugin_module_export(
            self,
            imported_module,
        ):
            if not imported_module:
                return {}

            module_export = (
                imported_module.export()
            )

            return (
                module_export
            )

    _PluginManager = __PluginManager
    _allocate_module = lambda: None


def PluginManager():
    if _PluginManager is None:
        _allocate_module()

    return _PluginManager

# PluginManager()
