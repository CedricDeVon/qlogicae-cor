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


def _allocate():
    global _allocate
    global _PluginManager

    class __PluginManager:
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
        def collection(self):
            return self._collection

        @collection.setter
        def collection(self, value):
            self._collection = value

        def construct(self):
            global _sys
            global _pathlib
            global _importlib_util
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
            _PythonRuntimeUtilityManager = (
                PythonRuntimeUtilityManager().get_singleton
            )

            if (
                _PythonRuntimeUtilityManager()
                    .is_allocated_during_object_construction
            ):
                _ObjectMergeManager()
                _PythonModuleManager()

            self._collection = {}

            return True

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
                self.read_imported_modules(
                    options
                )
            )
            raw_module_exports = (
                self.read_raw_module_exports(
                    imported_modules
                )
            )
            collection = (
                self.setup_merged_raw_module_exports(
                    raw_module_exports
                )
            )
            self._collection = (
                collection
            )

            return True

        def shutdown(self):
            return True

        def read_imported_modules(
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

        def read_raw_module_exports(
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
    _allocate = lambda: None


def PluginManager():
    if _PluginManager is None:
        _allocate()

    return _PluginManager

# PluginManager()
