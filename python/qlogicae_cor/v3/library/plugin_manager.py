__all__ = (
    "PluginManager",
)

_types = None
_PluginManager = None
_ObjectMergeManager = None
_PythonModuleManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _PluginManager

    class __PluginManager:
        __slots__ = (
            "_module_exports",
        )

        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

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

        def construct(self):
            global _ExternalDependencyManager
            global _ObjectMergeManager
            global _PythonModuleManager
            global _types

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _types = (
                _ExternalDependencyManager().import_module(
                    path="types",
                )
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

            self._module_exports = {}

            return True

        def setup(
            self,
            **kwargs,
        ):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            imported_modules = (
                self.read_imported_modules(
                    kwargs
                )
            )
            raw_module_exports = (
                self.read_raw_module_exports(
                    imported_modules
                )
            )

            module_exports = (
                self.setup_merged_raw_module_exports(
                    kwargs,
                    raw_module_exports
                )
            )

            self._module_exports = (
                module_exports
            )

            return True

        def shutdown(self):
            return True

        def write_module_exports(
            self,
            value
        ):
            if not isinstance(value, (dict)) or not value:
                raise ValueError("'value' must be a non-empty dictionary")

            self._module_exports = (
                value
            )

            return True

        def remove_module_exports(
            self,
        ):
            self._module_exports = {}

            return True

        def read_module_exports(
            self,
        ):
            return (
                self._module_exports
            )

        def read_imported_modules(
            self,
            options,
        ):
            if not isinstance(options, (dict)) or not options:
                raise ValueError("'options' must be a non-empty dictionary")

            target_filesystem_paths = (
                options.get("target_filesystem_paths", tuple()) or tuple()
            )
            is_recursive = (
                options.get("is_recursive", True)
            )
            imported_modules = (
                options.get("imported_modules", tuple()) or tuple()
            )

            output_imported_modules = tuple(
                _PythonModuleManager()
                    .get_singleton()
                    .read_imported_modules(
                        target_filesystem_paths,
                        is_recursive
                    )
            )

            outputs = (
                imported_modules + output_imported_modules
            )

            return (
                outputs
            )

        def read_raw_module_exports(
            self,
            targets
        ):
            if not isinstance(targets, (tuple, list)) or not targets:
                raise ValueError("'targets' must either be a non-empty tuple or list")

            raw_module_exports = [
                self.read_plugin_module_export(
                    imported_module
                ) for imported_module in targets
            ]

            raw_module_exports.sort(
                key=lambda item: (item.get('object_merge', {}) or {}).get('level', 0)
            )

            return tuple(
                raw_module_exports
            )

        def setup_merged_raw_module_exports(
            self,
            options,
            targets
        ):
            if not isinstance(options, (dict)):
                raise ValueError("'options' must be a dictionary")

            if not isinstance(targets, (tuple, list)) or not targets:
                raise ValueError("'targets' must either be a non-empty tuple or list")

            object_merge_manager = (
                _ObjectMergeManager().get_singleton()
            )

            raw_export_data = (
                options.get("raw_export_data", tuple()) or tuple()
            )
            initial_export_data = (
                options.get("initial_export_data", {}) or {}
            )

            targets = (
                tuple(targets) + raw_export_data
            )

            module_exports = initial_export_data
            for target in targets:
                if not isinstance(target, (dict)):
                    raise ValueError("'target' must be a dictionary")

                module_exports = (
                    object_merge_manager.deep_merge(
                        module_exports,
                        target
                    )
                )

            return (
                module_exports
            )


        def read_plugin_module_export(
            self,
            target,
        ):
            if not isinstance(target, (_types().ModuleType)) or not target:
                raise ValueError("'target' must be a non-empty module")

            module_export = (
                target.export()
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
