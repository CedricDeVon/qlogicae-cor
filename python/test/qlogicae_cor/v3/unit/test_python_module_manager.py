
import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from qlogicae_cor.v3.library import python_module_manager as target


MODULE = importlib.import_module(
    "qlogicae_cor.v3.library.python_module_manager"
)

MODULE_PREFIX = "qlogicae_test_python_module_manager_"

@pytest.fixture
def manager_class() -> type:
    return target.PythonModuleManager()


@pytest.fixture
def manager(manager_class: type) -> Any:
    return manager_class()


@pytest.fixture
def module_directory(tmp_path: Path) -> Path:
    return tmp_path / "modules"


@pytest.fixture
def isolated_modules():
    original_modules = set(sys.modules)

    yield

    for module_name in tuple(sys.modules):
        if module_name not in original_modules:
            if module_name.startswith("test_python_module_"):
                sys.modules.pop(module_name, None)


def write_module(
    directory: Path,
    module_name: str,
    content: str,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    module_path = directory / f"{module_name}.py"
    module_path.write_text(content, encoding="utf-8")
    return module_path


class PythonModuleManagerAdditionalAllocationTest:

    def test_should_allocate_class_after_module_reload(self) -> None:
        reloaded_module = importlib.reload(target)

        assert reloaded_module._PythonModuleManager is None

        manager_class = reloaded_module.PythonModuleManager()

        assert isinstance(manager_class, type)
        assert reloaded_module._PythonModuleManager is manager_class

    def test_should_replace_allocator_after_first_allocation(
        self,
        manager_class: type,
    ) -> None:
        assert target._PythonModuleManager is manager_class
        assert callable(target._allocate)

        assert target._allocate() is None

    def test_should_return_same_class_after_multiple_allocations(
        self,
        manager_class: type,
    ) -> None:
        first_class = target.PythonModuleManager()
        second_class = target.PythonModuleManager()

        assert first_class is manager_class
        assert second_class is manager_class

    def test_should_initialize_dependencies_when_construct_is_called(
        self,
        manager: Any,
    ) -> None:
        assert callable(target._ExternalDependencyManager)
        assert callable(target._sys)
        assert callable(target._pathlib)
        assert callable(target._importlib_util)

        assert target._sys() is sys
        assert target._pathlib() is importlib.import_module("pathlib")
        assert (
            target._importlib_util()
            is importlib.import_module("importlib.util")
        )


class PythonModuleManagerAdditionalLifecycleTest:

    def test_should_initialize_instance_when_construct_is_called(
        self,
        manager_class: type,
    ) -> None:
        instance = manager_class()

        assert instance.construct() is True
        assert callable(target._ExternalDependencyManager)

    def test_should_return_true_when_setup_receives_nested_values(
        self,
        manager: Any,
    ) -> None:
        result = manager.setup(
            values={
                "nested": {
                    "items": (1, 2, 3),
                },
            },
            enabled=True,
        )

        assert result is True

    def test_should_return_true_when_shutdown_is_repeated(
        self,
        manager: Any,
    ) -> None:
        assert manager.shutdown() is True
        assert manager.shutdown() is True

    def test_should_return_instance_when_context_manager_is_nested(
        self,
        manager_class: type,
    ) -> None:
        with manager_class() as first_instance:
            with manager_class() as second_instance:
                assert isinstance(first_instance, manager_class)
                assert isinstance(second_instance, manager_class)

    def test_should_preserve_exception_when_context_manager_exits(
        self,
        manager_class: type,
    ) -> None:
        with pytest.raises(
            ValueError,
        ):
            with manager_class():
                raise ValueError("expected failure")


class PythonModuleManagerAdditionalDiscoveryTest:

    def test_should_return_empty_tuple_when_directory_contains_no_python_files(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        module_directory.mkdir()

        (module_directory / "example.txt").write_text(
            "ignored",
            encoding="utf-8",
        )

        assert manager.read_imported_modules([module_directory]) == ()

    def test_should_skip_root_init_without_loading_other_modules(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        module_directory.mkdir()

        write_module(
            module_directory,
            "__init__",
            "package_value = 10",
        )

        result = manager.read_imported_modules([module_directory])

        assert result == ()

    def test_should_load_nested_package_initializers(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        package_directory = module_directory / "test_python_module_package"
        nested_directory = package_directory / "nested"

        write_module(
            package_directory,
            "__init__",
            "package_value = 10",
        )
        write_module(
            nested_directory,
            "__init__",
            "nested_value = 20",
        )

        result = manager.read_imported_modules([module_directory])

        modules = {
            item.__name__: item
            for item in result
        }

        assert "test_python_module_package" in modules
        assert "test_python_module_package.nested" in modules

        assert (
            modules["test_python_module_package"].package_value
            == 10
        )
        assert (
            modules["test_python_module_package.nested"].nested_value
            == 20
        )

    def test_should_load_nested_module_without_package_initializer(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        nested_directory = module_directory / "test_python_module_nested"

        write_module(
            nested_directory,
            "child",
            "value = 42",
        )

        result = manager.read_imported_modules([module_directory])

        assert len(result) == 1
        assert result[0].__name__ == (
            "test_python_module_nested.child"
        )
        assert result[0].value == 42

    def test_should_load_modules_from_relative_path(
        self,
        manager: Any,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        directory = tmp_path / "relative"
        directory.mkdir()

        write_module(
            directory,
            "test_python_module_relative",
            "value = 42",
        )

        monkeypatch.chdir(tmp_path)

        result = manager.read_imported_modules(["relative"])

        assert len(result) == 1
        assert result[0].value == 42

    def test_should_skip_duplicate_files_across_overlapping_directories(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        nested_directory = module_directory / "nested"

        write_module(
            nested_directory,
            "test_python_module_duplicate",
            "value = 42",
        )

        result = manager.read_imported_modules(
            [module_directory, nested_directory],
        )

        assert len(result) == 1

    def test_should_load_modules_from_tuple_of_paths(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_tuple",
            "value = 42",
        )

        result = manager.read_imported_modules((module_directory,))

        assert len(result) == 1
        assert result[0].value == 42

    def test_should_skip_non_directory_paths(
        self,
        manager: Any,
        tmp_path: Path,
    ) -> None:
        file_path = tmp_path / "ordinary.txt"
        file_path.write_text("value", encoding="utf-8")

        result = manager.read_imported_modules(
            [file_path, tmp_path / "missing"],
        )

        assert result == ()

    def test_should_resolve_special_characters_in_module_content(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        expected_value = "特殊文字 !@#$%^&*()"

        write_module(
            module_directory,
            "test_python_module_special",
            f"value = {expected_value!r}",
        )

        result = manager.read_imported_modules([module_directory])

        assert result[0].value == expected_value

    def test_should_load_module_with_large_collection(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        values = tuple(range(10_000))

        write_module(
            module_directory,
            "test_python_module_collection",
            f"values = {values!r}",
        )

        result = manager.read_imported_modules([module_directory])

        assert result[0].values == values
        assert len(result[0].values) == 10_000


class PythonModuleManagerAdditionalImportTest:

    def test_should_raise_import_error_when_spec_is_missing(
        self,
        manager: Any,
        module_directory: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_missing_spec",
            "value = 42",
        )

        class ImportUtility:

            @staticmethod
            def spec_from_file_location(
                module_name: str,
                file_path: Path,
            ) -> None:
                return None

        monkeypatch.setattr(
            target,
            "_importlib_util",
            lambda: ImportUtility,
        )

        with pytest.raises(
            ImportError,
        ):
            manager.read_imported_modules([module_directory])

    def test_should_raise_import_error_when_spec_has_no_loader(
        self,
        manager: Any,
        module_directory: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_missing_loader",
            "value = 42",
        )

        class ImportUtility:

            @staticmethod
            def spec_from_file_location(
                module_name: str,
                file_path: Path,
            ) -> SimpleNamespace:
                return SimpleNamespace(loader=None)

        monkeypatch.setattr(
            target,
            "_importlib_util",
            lambda: ImportUtility,
        )

        with pytest.raises(
            ImportError,
        ):
            manager.read_imported_modules([module_directory])

    def test_should_remove_failed_module_after_base_exception(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_base_exception",
            "raise KeyboardInterrupt('interrupted')",
        )

        with pytest.raises(KeyboardInterrupt, match="interrupted"):
            manager.read_imported_modules([module_directory])

        assert "test_python_module_base_exception" not in sys.modules

    def test_should_remove_failed_module_after_system_exit(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_system_exit",
            "raise SystemExit(1)",
        )

        with pytest.raises(SystemExit):
            manager.read_imported_modules([module_directory])

        assert "test_python_module_system_exit" not in sys.modules

    def test_should_preserve_successful_modules_after_later_failure(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_success",
            "value = 42",
        )

        write_module(
            module_directory,
            "test_python_module_failure",
            "raise RuntimeError('failure')",
        )

        with pytest.raises(RuntimeError, match="failure"):
            manager.read_imported_modules([module_directory])

        assert "test_python_module_success" in sys.modules
        assert "test_python_module_failure" not in sys.modules

    def test_should_replace_existing_module_registration(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        module_name = "test_python_module_replacement"

        write_module(
            module_directory,
            module_name,
            "value = 10",
        )

        first_result = manager.read_imported_modules([module_directory])
        first_module = first_result[0]

        write_module(
            module_directory,
            module_name,
            "value = 20",
        )

        second_result = manager.read_imported_modules([module_directory])

        assert second_result[0].value == 20
        assert second_result[0] is not first_module
        assert sys.modules[module_name] is second_result[0]

    def test_should_return_module_instances(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_instance",
            "value = 42",
        )

        result = manager.read_imported_modules([module_directory])

        assert all(
            isinstance(item, ModuleType)
            for item in result
        )


class PythonModuleManagerAdditionalLoadedModulesTest:

    def test_should_return_generator_without_eager_materialization(
        self,
        manager: Any,
    ) -> None:
        result = manager.read_loaded_modules()

        assert not isinstance(result, tuple)
        assert iter(result) is result

    def test_should_return_current_module_registry_names(
        self,
        manager: Any,
    ) -> None:
        result = tuple(manager.read_loaded_modules())

        assert "sys" in result
        assert "builtins" in result

    def test_should_reflect_modules_added_after_generator_creation(
        self,
        manager: Any,
    ) -> None:
        result = manager.read_loaded_modules()
        module_name = "test_python_module_dynamic_registration"

        sys.modules[module_name] = ModuleType(module_name)

        try:
            assert module_name in tuple(result)
        finally:
            sys.modules.pop(module_name, None)

    def test_should_return_empty_iteration_when_registry_is_empty(
        self,
        manager: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        class EmptySystem:

            modules: dict[str, ModuleType] = {}

        monkeypatch.setattr(
            target,
            "_sys",
            lambda: EmptySystem,
        )

        assert tuple(manager.read_loaded_modules()) == ()


class PythonModuleManagerAdditionalStressTest:

    def test_should_load_modules_across_repeated_discovery_calls(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        module_count = 50

        for index in range(module_count):
            write_module(
                module_directory,
                f"test_python_module_stress_{index}",
                f"value = {index}",
            )

        for _ in range(3):
            result = manager.read_imported_modules([module_directory])

            assert len(result) == module_count
            assert sum(item.value for item in result) == 1225

    def test_should_handle_repeated_module_construction(
        self,
        manager_class: type,
    ) -> None:
        instances = tuple(
            manager_class()
            for _ in range(200)
        )

        assert len(instances) == 200
        assert len({id(instance) for instance in instances}) == 200

    def test_should_preserve_module_values_after_multiple_reads(
        self,
        manager: Any,
        module_directory: Path,
    ) -> None:
        write_module(
            module_directory,
            "test_python_module_repeated_read",
            "values = tuple(range(1000))",
        )

        first_result = manager.read_imported_modules([module_directory])
        second_result = manager.read_imported_modules([module_directory])

        assert first_result[0].values == tuple(range(1000))
        assert second_result[0].values == tuple(range(1000))
        assert first_result[0] is not second_result[0]


@pytest.fixture
def fresh_module():
    return importlib.reload(MODULE)


@pytest.fixture
def manager_class(fresh_module):
    return fresh_module.PythonModuleManager()


@pytest.fixture
def manager(manager_class):
    return manager_class()


@pytest.fixture
def module_registry():
    original = {
        name: module
        for name, module in sys.modules.items()
        if name.startswith(MODULE_PREFIX)
    }

    yield

    for name in tuple(sys.modules):
        if name.startswith(MODULE_PREFIX):
            sys.modules.pop(name, None)

    sys.modules.update(original)


def test_should_allocate_manager_class_once(fresh_module):
    manager_class = fresh_module.PythonModuleManager()

    assert manager_class is not None
    assert fresh_module.PythonModuleManager() is manager_class


def test_should_create_singleton_once(manager_class):
    first = manager_class.get_singleton()
    second = manager_class.get_singleton()

    assert first is second


def test_should_construct_manager_on_initialization(manager_class):
    instance = manager_class()

    assert instance is not None
    assert instance.construct() is True


def test_should_return_manager_from_context(manager_class):
    instance = manager_class()

    with instance as context:
        assert context is instance


def test_should_accept_empty_setup(manager):
    with pytest.raises(ValueError):
        manager.setup()


def test_should_accept_non_empty_setup(manager):
    assert manager.setup(enabled=True) is True


@pytest.mark.parametrize(
    "paths",
    (
        None,
        "directory",
        123,
        {},
        set(),
    ),
)
def test_should_reject_unsupported_path_containers(manager, paths):
    with pytest.raises(ValueError, match="tuple or list"):
        manager.read_imported_modules(paths)


@pytest.mark.parametrize(
    "recursive",
    (
        None,
        0,
        1,
        "true",
        [],
    ),
)
def test_should_reject_non_boolean_recursive_values(manager, recursive):
    with pytest.raises(ValueError, match="must be a boolean"):
        manager.read_imported_modules([], is_recursive=recursive)


@pytest.mark.parametrize("paths", ([], ()))
def test_should_return_empty_tuple_for_empty_paths(manager, paths):
    assert manager.read_imported_modules(paths) == ()


def test_should_skip_nonexistent_directories(manager, tmp_path):
    result = manager.read_imported_modules(
        [tmp_path / "missing"],
    )

    assert result == ()


def test_should_skip_files_in_non_recursive_mode(
    manager,
    tmp_path,
    module_registry,
):
    root = tmp_path / "source"
    nested = root / "nested"
    nested.mkdir(parents=True)

    (root / "top_level.py").write_text("VALUE = 1")
    (nested / "nested_module.py").write_text("VALUE = 2")

    modules = manager.read_imported_modules(
        [root],
        is_recursive=False,
    )

    assert len(modules) == 1
    assert modules[0].VALUE == 1


def test_should_import_nested_files_in_recursive_mode(
    manager,
    tmp_path,
    module_registry,
):
    root = tmp_path / "source"
    nested = root / "nested"
    nested.mkdir(parents=True)

    (root / "top_level.py").write_text("VALUE = 1")
    (nested / "nested_module.py").write_text("VALUE = 2")

    modules = manager.read_imported_modules(
        [root],
        is_recursive=True,
    )

    assert len(modules) == 2
    assert {module.VALUE for module in modules} == {1, 2}


def test_should_ignore_duplicate_folder_paths(
    manager,
    tmp_path,
    module_registry,
):
    root = tmp_path / "source"
    root.mkdir()

    (root / "example.py").write_text("VALUE = 10")

    modules = manager.read_imported_modules(
        [root, root],
    )

    assert len(modules) == 1
    assert modules[0].VALUE == 10


def test_should_ignore_duplicate_files_from_overlapping_directories(
    manager,
    tmp_path,
    module_registry,
):
    root = tmp_path / "source"
    nested = root / "nested"
    nested.mkdir(parents=True)

    (nested / "example.py").write_text("VALUE = 10")

    modules = manager.read_imported_modules(
        [root, nested],
    )

    assert len(modules) == 1
    assert modules[0].VALUE == 10


def test_should_skip_root_package_initializer(
    manager,
    tmp_path,
    module_registry,
):
    root = tmp_path / "source"
    root.mkdir()

    (root / "__init__.py").write_text("VALUE = 10")

    modules = manager.read_imported_modules([root])

    assert modules == ()


def test_should_register_imported_module(
    manager,
    tmp_path,
    module_registry,
):
    root = tmp_path / "source"
    root.mkdir()

    module_name = f"{MODULE_PREFIX}registered"
    (root / f"{module_name}.py").write_text("VALUE = 10")

    modules = manager.read_imported_modules([root])

    assert len(modules) == 1
    assert sys.modules[module_name] is modules[0]



def test_should_remove_module_registration_after_base_exception(
    manager,
    tmp_path,
    module_registry,
):
    root = tmp_path / "source"
    root.mkdir()

    module_name = f"{MODULE_PREFIX}interrupted"
    (root / f"{module_name}.py").write_text(
        "raise KeyboardInterrupt"
    )

    with pytest.raises(KeyboardInterrupt):
        manager.read_imported_modules([root])

    assert module_name not in sys.modules


@pytest.mark.parametrize(
    "spec",
    (
        None,
        SimpleNamespace(loader=None),
    ),
)
def test_should_raise_when_module_spec_is_invalid(
    manager,
    tmp_path,
    module_registry,
    monkeypatch,
    spec,
):
    root = tmp_path / "source"
    root.mkdir()

    (root / f"{MODULE_PREFIX}invalid_spec.py").write_text(
        "VALUE = 1"
    )

    utility = SimpleNamespace(
        spec_from_file_location=lambda *args: spec,
    )

    monkeypatch.setattr(
        MODULE,
        "_importlib_util",
        lambda: utility,
    )

    with pytest.raises(ImportError, match="Cannot load module"):
        manager.read_imported_modules([root])


def test_should_return_loaded_module_names_as_generator(manager):
    result = manager.read_loaded_modules()

    assert iter(result) is result

    module_names = tuple(result)

    assert "sys" in module_names
    assert "pathlib" in module_names
    assert "importlib.util" in module_names


def test_should_return_true_when_shutdown_is_called(manager):
    assert manager.shutdown() is True


def test_should_return_same_manager_class_after_repeated_factory_calls(
    fresh_module,
):
    first = fresh_module.PythonModuleManager()
    second = fresh_module.PythonModuleManager()
    third = fresh_module.PythonModuleManager()

    assert first is second
    assert second is third
