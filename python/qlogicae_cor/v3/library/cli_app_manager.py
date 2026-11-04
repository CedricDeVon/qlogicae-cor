__all__ = (
    "CliAppManager",
)

_LogManager = None
_CliAppManager = None
_PluginManager = None
_CliCommandManager = None
_ValueCacheManager = None
_PythonRuntimeUtilityManager = None
_PersistentCacheStorageManager = None


def _allocate():
    global _allocate
    global _CliAppManager

    class __CliAppManager:
        __slots__ = (
            "_options",
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

        def construct(self):
            global _LogManager
            global _PluginManager
            global _ValueCacheManager
            global _CliCommandManager
            global _PythonRuntimeUtilityManager
            global _PersistentCacheStorageManager

            from .cli_command_manager import CliCommandManager
            from .log_manager import LogManager
            from .persistent_cache_storage_manager import PersistentCacheStorageManager
            from .plugin_manager import PluginManager
            from .python_runtime_utility_manager import PythonRuntimeUtilityManager
            from .value_cache_manager import ValueCacheManager

            _LogManager = LogManager().get_singleton
            _PluginManager = PluginManager().get_singleton
            _ValueCacheManager = ValueCacheManager().get_singleton
            _CliCommandManager = CliCommandManager().get_singleton
            _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager().get_singleton
            _PersistentCacheStorageManager = (
                PersistentCacheStorageManager().get_singleton
            )

            if (
                _PythonRuntimeUtilityManager()
                    .is_allocated_during_object_construction
            ):
                _PluginManager()
                _CliCommandManager()

            self._options = {}

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            return True

        def shutdown(
            self,
            *,
            wait=True,
        ):
            if self._thread_executor is not None:
                self._thread_executor.shutdown(
                    wait=wait,
                )

                self._thread_executor = None

            if self._process_executor is not None:
                self._process_executor.shutdown(
                    wait=wait,
                )

                self._process_executor = None

            return True

        # def run_application(self, **kwargs):
        #     if not kwargs:
        #         return (
        #             self.evaluate_output(
        #                 False
        #             )
        #         )

        #     options = (
        #         kwargs.get(
        #             "options",
        #             {}
        #         ) or {}
        #     )
        #     if not options:
        #         return (
        #             self.evaluate_output(
        #                 result
        #             )
        #         )

        #     self._options = (
        #         options
        #     )

        #     result = True

        #     result = (
        #         self.setup_plugin_module_exports()
        #     ) and result
        #     result = (
        #         self.setup_command_parser()
        #     ) and result
        #     result = (
        #         self.run_command_parser()
        #     ) and result

        #     return (
        #         self.evaluate_output(
        #             result
        #         )
        #     )

        # def setup_plugin_module_exports(self):
        #     plugin_manager = (
        #         _PluginManager()
        #     )

        #     options_extraction = (
        #         self._options.get(
        #             "plugin",
        #             {}
        #         ) or {}
        #     )
        #     options_extraction = (
        #         options_extraction.get(
        #             "extraction",
        #             {}
        #         ) or {}
        #     )

        #     result = (
        #         plugin_manager.setup_imported_modules(
        #             options=options_extraction
        #         )
        #     )

        #     return result

        # def setup_command_parser(self):
        #     cli_command_manager = (
        #         _CliCommandManager()
        #     )
        #     plugin_manager = (
        #         _PluginManager()
        #     )

        #     plugin_module_exports = (
        #         plugin_manager.module_exports
        #     )
        #     cli_data = (
        #         plugin_module_exports.get(
        #             "cli",
        #             {}
        #         ) or {}
        #     )

        #     result = (
        #         cli_command_manager.setup_command_parser(
        #             **cli_data
        #         )
        #     )

        #     return result

        # def run_command_parser(self):
        #     cli_command_manager = (
        #         _CliCommandManager()
        #     )

        #     result = (
        #         cli_command_manager
        #             .run_command_parser()
        #     )

        #     return result

        # def evaluate_output(self, value):
        #     return 0 if value else 1


    _CliAppManager = __CliAppManager
    _allocate = lambda: None


def CliAppManager():
    if _CliAppManager is None:
        _allocate()

    return _CliAppManager


# CliAppManager().get_singleton().run_application(
#     options={
#         "plugin": {
#             "extraction": {
#                 "target_filesystem_paths": (
#                     "./qlogicae_cor/v3/library/plugin"
#                 ),
#             }
#         },
#     }
# )
