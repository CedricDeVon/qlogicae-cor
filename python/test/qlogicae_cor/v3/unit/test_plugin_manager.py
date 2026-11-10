
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

import qlogicae_cor.v3.library.plugin_manager as plugin_module
from qlogicae_cor.v3.library.external_dependency_manager import (
    ExternalDependencyManager,
)
from qlogicae_cor.v3.library.plugin_manager import PluginManager


@pytest.fixture
def manager_class():
    manager_type = PluginManager()
    manager_type._singleton = None

    yield manager_type

    manager_type._singleton = None


@pytest.fixture
def manager(manager_class):
    return manager_class()


@pytest.fixture
def plugin_module_factory():
    def create_module(export_value):
        module = ModuleType("test_plugin")
        module.export = lambda: export_value
        return module

    return create_module


@pytest.fixture
def python_module_manager(monkeypatch):
    dependency = MagicMock()
    dependency.read_imported_modules.return_value = ()

    singleton = SimpleNamespace(
        read_imported_modules=dependency.read_imported_modules
    )

    manager_factory = SimpleNamespace(
        get_singleton=lambda: singleton
    )

    monkeypatch.setattr(
        plugin_module,
        "_PythonModuleManager",
        lambda: manager_factory,
    )

    return dependency


@pytest.fixture
def object_merge_manager(monkeypatch):
    dependency = MagicMock()
    dependency.deep_merge.side_effect = (
        lambda first, second: {**first, **second}
    )

    singleton = SimpleNamespace(
        deep_merge=dependency.deep_merge
    )

    manager_factory = SimpleNamespace(
        get_singleton=lambda: singleton
    )

    monkeypatch.setattr(
        plugin_module,
        "_ObjectMergeManager",
        lambda: manager_factory,
    )

    return dependency


class TestPluginManagerLifecycle:
    def test_should_construct_manager(self, manager):
        assert manager.module_exports == {}

    def test_should_return_manager_class(self):
        assert callable(PluginManager())

    def test_should_create_singleton(self, manager_class):
        first = manager_class.get_singleton()
        second = manager_class.get_singleton()

        assert first is second

    def test_should_construct_new_singleton_after_reset(
        self,
        manager_class,
    ):
        first = manager_class.get_singleton()
        manager_class._singleton = None
        second = manager_class.get_singleton()

        assert first is not second

    def test_should_enter_context_manager(self, manager):
        assert manager.__enter__() is manager

    def test_should_return_true_when_shutdown(self, manager):
        assert manager.shutdown() is True

    def test_should_use_external_dependency_manager(self, manager):
        dependency_manager_class = ExternalDependencyManager()
        dependency_manager = dependency_manager_class.get_singleton()

        assert dependency_manager is not None

    def test_should_call_shutdown_when_exit_is_invoked(self, manager):
        shutdown = MagicMock(return_value=True)

        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(type(manager), "shutdown", shutdown)

        try:
            result = manager.__exit__(None, None, None)
        finally:
            monkeypatch.undo()

        assert result is None
        shutdown.assert_called_once_with()
        
class TestPluginManagerProperties:
    def test_should_read_module_exports(self, manager):
        assert manager.module_exports == {}

    def test_should_write_module_exports(self, manager):
        expected = {"first": 1}

        manager.module_exports = expected

        assert manager.module_exports is expected

    def test_should_preserve_assigned_dictionary(self, manager):
        expected = {"first": {"second": 2}}

        manager.module_exports = expected

        assert manager.read_module_exports() is expected

    def test_should_allow_empty_module_exports(self, manager):
        manager.module_exports = {}

        assert manager.module_exports == {}


class TestPluginManagerWrites:
    def test_should_write_module_exports(self, manager):
        expected = {"first": 1}

        assert manager.write_module_exports(expected) is True
        assert manager.module_exports == expected

    def test_should_preserve_dictionary_reference(self, manager):
        expected = {"first": 1}

        manager.write_module_exports(expected)

        assert manager.module_exports is expected

    @pytest.mark.parametrize(
        "value",
        [
            None,
            (),
            [],
            "",
            0,
            False,
            object(),
        ],
    )
    def test_should_reject_invalid_module_exports(self, manager, value):
        with pytest.raises(
            ValueError,
        ):
            manager.write_module_exports(value)

    def test_should_remove_module_exports(self, manager):
        manager.write_module_exports({"first": 1})

        assert manager.remove_module_exports() is True
        assert manager.module_exports == {}

    def test_should_read_module_exports(self, manager):
        expected = {"first": 1}
        manager.write_module_exports(expected)

        assert manager.read_module_exports() is expected

    def test_should_return_true_when_removing_empty_exports(self, manager):
        assert manager.remove_module_exports() is True
        assert manager.module_exports == {}


class TestPluginManagerImportedModules:
    def test_should_read_imported_modules(
        self,
        manager,
        python_module_manager,
    ):
        imported_modules = (ModuleType("first"), ModuleType("second"))
        python_module_manager.read_imported_modules.return_value = (
            imported_modules
        )

        result = manager.read_imported_modules(
            {"target_filesystem_paths": ("plugins",)}
        )

        assert result == imported_modules
        python_module_manager.read_imported_modules.assert_called_once_with(
            ("plugins",),
            True,
        )

    def test_should_use_recursive_discovery_by_default(
        self,
        manager,
        python_module_manager,
    ):
        manager.read_imported_modules({"target_filesystem_paths": ("plugins",)})

        python_module_manager.read_imported_modules.assert_called_once_with(
            ("plugins",),
            True,
        )

    def test_should_disable_recursive_discovery(
        self,
        manager,
        python_module_manager,
    ):
        manager.read_imported_modules(
            {
                "target_filesystem_paths": ("plugins",),
                "is_recursive": False,
            }
        )

        python_module_manager.read_imported_modules.assert_called_once_with(
            ("plugins",),
            False,
        )

    def test_should_use_empty_paths_by_default(
        self,
        manager,
        python_module_manager,
    ):
        manager.read_imported_modules({"modules": ()})

        python_module_manager.read_imported_modules.assert_called_once_with(
            (),
            True,
        )

    def test_should_append_explicit_modules(
        self,
        manager,
        python_module_manager,
    ):
        discovered = ModuleType("discovered")
        explicit = ModuleType("explicit")
        python_module_manager.read_imported_modules.return_value = (
            discovered,
        )

        result = manager.read_imported_modules(
            {"modules": (explicit,)}
        )

        assert result == (discovered, explicit)

    def test_should_return_explicit_modules_without_discovery_results(
        self,
        manager,
        python_module_manager,
    ):
        explicit = ModuleType("explicit")

        result = manager.read_imported_modules(
            {"modules": (explicit,)}
        )

        assert result == (explicit,)

    def test_should_return_empty_tuple_when_no_modules_are_found(
        self,
        manager,
        python_module_manager,
    ):
        result = manager.read_imported_modules(
            {"target_filesystem_paths": ("plugins",)}
        )

        assert result == ()

    @pytest.mark.parametrize(
        "options",
        [
            None,
            (),
            [],
            "",
            0,
            False,
            object(),
            {},
        ],
    )
    def test_should_reject_invalid_options(self, manager, options):
        with pytest.raises(
            ValueError,
        ):
            manager.read_imported_modules(options)


class TestPluginManagerRawExports:
    def test_should_read_plugin_module_export(
        self,
        manager,
        plugin_module_factory,
    ):
        module = plugin_module_factory({"first": 1})

        assert manager.read_plugin_module_export(module) == {"first": 1}

    def test_should_call_module_export_once(
        self,
        manager,
    ):
        module = ModuleType("test_plugin")
        module.export = MagicMock(return_value={"first": 1})

        result = manager.read_plugin_module_export(module)

        assert result == {"first": 1}
        module.export.assert_called_once_with()

    def test_should_read_raw_module_exports(
        self,
        manager,
        plugin_module_factory,
    ):
        first = plugin_module_factory({"first": 1})
        second = plugin_module_factory({"second": 2})

        result = manager.read_raw_module_exports((first, second))

        assert result == (
            {"first": 1},
            {"second": 2},
        )

    def test_should_read_raw_exports_from_list(
        self,
        manager,
        plugin_module_factory,
    ):
        first = plugin_module_factory({"first": 1})
        second = plugin_module_factory({"second": 2})

        result = manager.read_raw_module_exports([first, second])

        assert result == (
            {"first": 1},
            {"second": 2},
        )

    def test_should_reject_empty_targets(self, manager):
        with pytest.raises(
            ValueError,
        ):
            manager.read_raw_module_exports(())

    def test_should_reject_empty_target_list(self, manager):
        with pytest.raises(
            ValueError,
        ):
            manager.read_raw_module_exports([])

    @pytest.mark.parametrize(
        "target",
        [
            None,
            {},
            (),
            [],
            "",
            0,
            False,
            object(),
        ],
    )
    def test_should_reject_invalid_plugin_module(self, manager, target):
        with pytest.raises(
            ValueError,
        ):
            manager.read_plugin_module_export(target)

    def test_should_propagate_export_exception(self, manager):
        module = ModuleType("test_plugin")

        def export():
            raise RuntimeError("export failure")

        module.export = export

        with pytest.raises(RuntimeError, match="export failure"):
            manager.read_plugin_module_export(module)

    def test_should_propagate_missing_export_attribute(self, manager):
        module = ModuleType("test_plugin")

        with pytest.raises(AttributeError):
            manager.read_plugin_module_export(module)


class TestPluginManagerMerge:
    def test_should_merge_single_target(
        self,
        manager,
        object_merge_manager,
    ):
        result = manager.setup_merged_raw_module_exports(
            {},
            ({"first": 1},),
        )

        assert result == {"first": 1}
        object_merge_manager.deep_merge.assert_called_once_with(
            {},
            {"first": 1},
        )

    def test_should_merge_multiple_targets(
        self,
        manager,
        object_merge_manager,
    ):
        result = manager.setup_merged_raw_module_exports(
            {},
            (
                {"first": 1},
                {"second": 2},
                {"third": 3},
            ),
        )

        assert result == {
            "first": 1,
            "second": 2,
            "third": 3,
        }

        assert object_merge_manager.deep_merge.call_count == 3

    def test_should_merge_nested_dictionaries(
        self,
        manager,
        object_merge_manager,
    ):
        object_merge_manager.deep_merge.side_effect = (
            lambda first, second: {
                **first,
                **{
                    key: (
                        {
                            **first[key],
                            **value,
                        }
                        if isinstance(first.get(key), dict)
                        and isinstance(value, dict)
                        else value
                    )
                    for key, value in second.items()
                },
            }
        )

        result = manager.setup_merged_raw_module_exports(
            {},
            (
                {"config": {"first": 1}},
                {"config": {"second": 2}},
            ),
        )

        assert result == {
            "config": {
                "first": 1,
                "second": 2,
            }
        }

    def test_should_merge_raw_data(
        self,
        manager,
        object_merge_manager,
    ):
        result = manager.setup_merged_raw_module_exports(
            {"raw_data": ({"second": 2},)},
            ({"first": 1},),
        )

        assert result == {
            "first": 1,
            "second": 2,
        }

        assert object_merge_manager.deep_merge.call_args_list == [
            call({}, {"first": 1}),
            call({"first": 1}, {"second": 2}),
        ]

    def test_should_merge_multiple_raw_data_entries(
        self,
        manager,
        object_merge_manager,
    ):
        result = manager.setup_merged_raw_module_exports(
            {
                "raw_data": (
                    {"second": 2},
                    {"third": 3},
                )
            },
            ({"first": 1},),
        )

        assert result == {
            "first": 1,
            "second": 2,
            "third": 3,
        }

        assert object_merge_manager.deep_merge.call_count == 3

    def test_should_allow_missing_raw_data(
        self,
        manager,
        object_merge_manager,
    ):
        result = manager.setup_merged_raw_module_exports(
            {},
            ({"first": 1},),
        )

        assert result == {"first": 1}

    def test_should_allow_empty_raw_data(
        self,
        manager,
        object_merge_manager,
    ):
        result = manager.setup_merged_raw_module_exports(
            {"raw_data": ()},
            ({"first": 1},),
        )

        assert result == {"first": 1}

    def test_should_reject_empty_targets(self, manager):
        with pytest.raises(
            ValueError,
        ):
            manager.setup_merged_raw_module_exports({}, ())

    def test_should_reject_empty_target_list(self, manager):
        with pytest.raises(
            ValueError,
        ):
            manager.setup_merged_raw_module_exports({}, [])

    @pytest.mark.parametrize(
        "target",
        [
            None,
            {},
            (),
            [],
            "",
            0,
            False,
            object(),
        ],
    )
    def test_should_reject_invalid_merge_targets(self, manager, target):
        with pytest.raises(
            ValueError,
        ):
            manager.setup_merged_raw_module_exports(
                {},
                (target,),
            )

    @pytest.mark.parametrize(
        "raw_data",
        [
            (None,),
            ({},),
            ((),),
            ([],),
            ("",),
            (0,),
            (False,),
        ],
    )
    def test_should_reject_invalid_raw_data_entries(
        self,
        manager,
        raw_data,
    ):
        with pytest.raises(
            ValueError,
        ):
            manager.setup_merged_raw_module_exports(
                {"raw_data": raw_data},
                ({"first": 1},),
            )

    @pytest.mark.parametrize(
        "options",
        [
            None,
            (),
            [],
            "",
            0,
            False,
            object(),
        ],
    )

    def test_should_reject_invalid_options(self, manager, options):
        with pytest.raises(
            ValueError,
        ):
            manager.setup_merged_raw_module_exports(
                options,
                ({"first": 1},),
            )

    def test_should_propagate_merge_exception(
        self,
        manager,
        object_merge_manager,
    ):
        object_merge_manager.deep_merge.side_effect = RuntimeError(
            "merge failure"
        )

        with pytest.raises(RuntimeError, match="merge failure"):
            manager.setup_merged_raw_module_exports(
                {},
                ({"first": 1},),
            )

    def test_should_stop_merging_after_exception(
        self,
        manager,
        object_merge_manager,
    ):
        object_merge_manager.deep_merge.side_effect = RuntimeError(
            "merge failure"
        )

        with pytest.raises(RuntimeError):
            manager.setup_merged_raw_module_exports(
                {},
                (
                    {"first": 1},
                    {"second": 2},
                    {"third": 3},
                ),
            )

        object_merge_manager.deep_merge.assert_called_once()

    def test_should_merge_large_number_of_targets(
        self,
        manager,
        object_merge_manager,
    ):
        targets = tuple(
            {f"key_{index}": index}
            for index in range(500)
        )

        result = manager.setup_merged_raw_module_exports(
            {},
            targets,
        )

        assert len(result) == 500
        assert result["key_0"] == 0
        assert result["key_499"] == 499
        assert object_merge_manager.deep_merge.call_count == 500


class TestPluginManagerSetup:
    def test_should_setup_from_explicit_modules(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        first = plugin_module_factory({"first": 1})
        second = plugin_module_factory({"second": 2})

        result = manager.setup(modules=(first, second))

        assert result is True
        assert manager.module_exports == {
            "first": 1,
            "second": 2,
        }

    def test_should_setup_from_discovered_modules(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        first = plugin_module_factory({"first": 1})
        second = plugin_module_factory({"second": 2})

        python_module_manager.read_imported_modules.return_value = (
            first,
            second,
        )

        result = manager.setup(
            target_filesystem_paths=("plugins",)
        )

        assert result is True
        assert manager.module_exports == {
            "first": 1,
            "second": 2,
        }

    def test_should_setup_with_raw_data(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        module = plugin_module_factory({"first": 1})

        result = manager.setup(
            modules=(module,),
            raw_data=({"second": 2},),
        )

        assert result is True
        assert manager.module_exports == {
            "first": 1,
            "second": 2,
        }

    def test_should_setup_with_only_raw_data_and_explicit_module(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        module = plugin_module_factory({"first": 1})

        manager.setup(
            modules=(module,),
            raw_data=(
                {"second": 2},
                {"third": 3},
            ),
        )

        assert manager.module_exports == {
            "first": 1,
            "second": 2,
            "third": 3,
        }

    def test_should_replace_previous_module_exports(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        manager.module_exports = {"old": 1}

        module = plugin_module_factory({"new": 2})

        manager.setup(modules=(module,))

        assert manager.module_exports == {"new": 2}

    def test_should_preserve_previous_exports_when_discovery_fails(
        self,
        manager,
        python_module_manager,
    ):
        manager.module_exports = {"existing": 1}
        python_module_manager.read_imported_modules.side_effect = (
            RuntimeError("discovery failure")
        )

        with pytest.raises(RuntimeError, match="discovery failure"):
            manager.setup(target_filesystem_paths=("plugins",))

        assert manager.module_exports == {"existing": 1}

    def test_should_preserve_previous_exports_when_export_fails(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
    ):
        manager.module_exports = {"existing": 1}

        module = ModuleType("test_plugin")

        def export():
            raise RuntimeError("export failure")

        module.export = export

        with pytest.raises(RuntimeError, match="export failure"):
            manager.setup(modules=(module,))

        assert manager.module_exports == {"existing": 1}

    def test_should_preserve_previous_exports_when_merge_fails(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        manager.module_exports = {"existing": 1}
        object_merge_manager.deep_merge.side_effect = RuntimeError(
            "merge failure"
        )

        module = plugin_module_factory({"new": 2})

        with pytest.raises(RuntimeError, match="merge failure"):
            manager.setup(modules=(module,))

        assert manager.module_exports == {"existing": 1}

    def test_should_reject_empty_setup_arguments(self, manager):
        with pytest.raises(
            ValueError,
        ):
            manager.setup()

    def test_should_accept_nonempty_setup_options(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        module = plugin_module_factory({"first": 1})

        assert manager.setup(modules=(module,)) is True

    def test_should_propagate_invalid_raw_data(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
        plugin_module_factory,
    ):
        module = plugin_module_factory({"first": 1})

        with pytest.raises(
            ValueError,
        ):
            manager.setup(
                modules=(module,),
                raw_data=({},),
            )


class TestPluginManagerStress:
    def test_should_process_many_plugin_modules(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
    ):
        modules = []

        for index in range(500):
            module = ModuleType(f"plugin_{index}")
            module.export = lambda index=index: {
                f"plugin_{index}": index
            }
            modules.append(module)

        result = manager.setup(modules=tuple(modules))

        assert result is True
        assert len(manager.module_exports) == 500
        assert manager.module_exports["plugin_0"] == 0
        assert manager.module_exports["plugin_499"] == 499

    def test_should_process_repeated_setup_operations(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
    ):
        for index in range(100):
            module = ModuleType(f"plugin_{index}")
            module.export = lambda index=index: {"value": index}

            assert manager.setup(modules=(module,)) is True
            assert manager.module_exports == {"value": index}

    def test_should_process_many_raw_data_entries(
        self,
        manager,
        object_merge_manager,
    ):
        targets = ({"initial": 1},)
        raw_data = tuple(
            {f"key_{index}": index}
            for index in range(500)
        )

        result = manager.setup_merged_raw_module_exports(
            {"raw_data": raw_data},
            targets,
        )

        assert len(result) == 501
        assert result["initial"] == 1
        assert result["key_499"] == 499


class TestPluginManagerConcurrency:
    def test_should_support_concurrent_singleton_access(
        self,
        manager_class,
    ):
        barrier = threading.Barrier(16)

        def get_singleton():
            barrier.wait()
            return manager_class.get_singleton()

        with ThreadPoolExecutor(max_workers=16) as executor:
            instances = list(
                executor.map(
                    lambda _: get_singleton(),
                    range(16),
                )
            )

        assert all(
            instance is instances[0]
            for instance in instances
        )

    def test_should_support_concurrent_export_reads(self, manager):
        manager.module_exports = {"value": 1}

        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(
                executor.map(
                    lambda _: manager.read_module_exports(),
                    range(100),
                )
            )

        assert all(result == {"value": 1} for result in results)

    def test_should_support_concurrent_export_writes(self, manager):
        def write_export(index):
            return manager.write_module_exports(
                {f"key_{index}": index}
            )

        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(
                executor.map(write_export, range(100))
            )

        assert all(results)
        assert len(manager.module_exports) == 1

    def test_should_support_concurrent_independent_managers(
        self,
        manager_class,
    ):
        def construct_manager(index):
            instance = manager_class()
            instance.write_module_exports({f"key_{index}": index})
            return instance

        with ThreadPoolExecutor(max_workers=16) as executor:
            instances = list(
                executor.map(construct_manager, range(100))
            )

        assert len(instances) == 100
        assert len({id(instance) for instance in instances}) == 100
        assert all(
            len(instance.module_exports) == 1
            for instance in instances
        )


class TestPluginManagerAsyncCompatibility:
    def test_should_support_async_setup(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
    ):
        async def run():
            module = ModuleType("async_plugin")
            module.export = lambda: {"async": True}

            return await asyncio.to_thread(
                manager.setup,
                modules=(module,),
            )

        assert asyncio.run(run()) is True
        assert manager.module_exports == {"async": True}

    def test_should_support_async_export_reads(self, manager):
        manager.module_exports = {"async": True}

        async def run():
            return await asyncio.to_thread(
                manager.read_module_exports
            )

        assert asyncio.run(run()) == {"async": True}

    def test_should_support_multiple_async_setup_calls(
        self,
        manager,
        python_module_manager,
        object_merge_manager,
    ):
        async def run(index):
            module = ModuleType(f"async_plugin_{index}")
            module.export = lambda index=index: {
                f"plugin_{index}": index
            }

            return await asyncio.to_thread(
                manager.setup,
                modules=(module,),
            )

        async def execute():
            return await asyncio.gather(
                *(run(index) for index in range(20))
            )

        results = asyncio.run(execute())

        assert all(results)
        assert len(manager.module_exports) == 1
