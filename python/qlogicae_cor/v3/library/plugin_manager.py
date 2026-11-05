__all__ = (
    "PluginManager",
)

_PluginManager = None
_ObjectMergeManager = None
_PythonModuleManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _PluginManager

    class __PluginManager:
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
        def collection(self):
            return self._collection

        @collection.setter
        def collection(self, value):
            self._collection = value

        def construct(self):
            global _ExternalDependencyManager
            global _ObjectMergeManager
            global _PythonModuleManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _ObjectMergeManager = (
                _ExternalDependencyManager().import_module(
                    path=".object_merge_manager",
                    package="qlogicae_cor.v3.library",
                    member="ObjectMergeManager",
                    is_member_callable=True,
                )
            )

            _PythonModuleManager = (
                _ExternalDependencyManager().import_module(
                    path=".python_module_manager",
                    package="qlogicae_cor.v3.library",
                    member="PythonModuleManager",
                    is_member_callable=True,
                )
            )

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
                    .get_singleton()
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
                _ObjectMergeManager().get_singleton()
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
