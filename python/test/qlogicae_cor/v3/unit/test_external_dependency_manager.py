import importlib
import importlib.util
import sys
import threading
import uuid

import pytest


from qlogicae_cor.v3.library import external_dependency_manager


@pytest.fixture(scope="module")
def module_under_test():
    return (
        external_dependency_manager
    )


@pytest.fixture
def manager_class(module_under_test):
    return module_under_test.ExternalDependencyManager()


@pytest.fixture
def manager(manager_class):
    return manager_class()

@pytest.fixture
def import_target_class(manager_class, module_under_test):
    manager_class()
    return module_under_test._ImportTarget

@pytest.fixture
def import_target(import_target_class):
    return import_target_class(path="json")


@pytest.fixture(autouse=True)
def reset_singleton(manager_class):
    manager_class._singleton = None
    yield
    manager_class._singleton = None


@pytest.fixture
def temporary_module(tmp_path, monkeypatch):
    module_name = f"temporary_module_{uuid.uuid4().hex}"
    module_path = tmp_path / f"{module_name}.py"
    module_path.write_text("VALUE = 123\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    yield module_name
    sys.modules.pop(module_name, None)


@pytest.fixture
def temporary_package(tmp_path, monkeypatch):
    package_name = f"temporary_package_{uuid.uuid4().hex}"
    package_path = tmp_path / package_name
    package_path.mkdir()
    (package_path / "__init__.py").write_text("PACKAGE_VALUE = 1\n", encoding="utf-8")
    (package_path / "dependency.py").write_text("VALUE = 456\n", encoding="utf-8")
    (package_path / "module.py").write_text(
        "from .dependency import VALUE\nMODULE_VALUE = VALUE\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    yield package_name
    for name in tuple(sys.modules):
        if name == package_name or name.startswith(f"{package_name}."):
            sys.modules.pop(name, None)


@pytest.mark.parametrize(
    ("kwargs", "expected_name"),
    [
        ({"path": "json"}, "json"),
        ({"path": "json", "name": "json_module"}, "json_module"),
        ({"path": "json", "name": ""}, "json"),
        ({"path": "json", "name": None}, "json"),
    ],
)
def test_import_target_construct_valid(import_target_class, kwargs, expected_name):
    target = import_target_class(**kwargs)
    assert target.name == expected_name
    assert target.path == "json"


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"path": ""},
        {"path": None},
        {"path": 123},
        {"path": []},
        {"path": {}},
    ],
)


def test_import_target_construct_rejects_invalid_path(import_target_class, kwargs):
    with pytest.raises(ValueError):
        import_target_class(**kwargs)


@pytest.mark.parametrize("name", [123, [], {}])
def test_import_target_construct_rejects_invalid_name(import_target_class, name):
    with pytest.raises(ValueError):
        import_target_class(path="json", name=name)


@pytest.mark.parametrize("package", [123, [], {}, True])
def test_import_target_construct_rejects_invalid_package(import_target_class, package):
    with pytest.raises(TypeError):
        import_target_class(path="json", package=package)


@pytest.mark.parametrize("package", [None, "", "json"])
def test_import_target_construct_accepts_valid_package(import_target_class, package):
    target = import_target_class(path="json", package=package)
    assert target.package == (package or None)


@pytest.mark.parametrize("value", [None, "", "module", "package.module"])
def test_import_target_package_setter_accepts_valid_values(import_target_class, value):
    target = import_target_class(path="json")
    target.package = value
    assert target.package == (value or None)


@pytest.mark.parametrize("value", [123, [], {}, True])
def test_import_target_package_setter_rejects_invalid_values(import_target, value):
    with pytest.raises(TypeError):
        import_target.package = value


@pytest.mark.parametrize("value", ["module", "another_module"])
def test_import_target_name_setter_accepts_valid_values(import_target, value):
    import_target.name = value
    assert import_target.name == value


@pytest.mark.parametrize("value", [None, "", 123, [], {}])
def test_import_target_name_setter_rejects_invalid_values(import_target, value):
    with pytest.raises(ValueError):
        import_target.name = value


@pytest.mark.parametrize("value", ["json", "platform"])
def test_import_target_path_setter_accepts_valid_values(import_target, value):
    import_target.path = value
    assert import_target.path == value


@pytest.mark.parametrize("value", [None, "", 123, [], {}])
def test_import_target_path_setter_rejects_invalid_values(import_target, value):
    with pytest.raises(ValueError):
        import_target.path = value


@pytest.mark.parametrize("value", [True, False])
def test_import_target_preallocation_setter_accepts_boolean(import_target, value):
    import_target.is_pre_allocated = value
    assert import_target.is_pre_allocated is value


@pytest.mark.parametrize("value", [None, 0, 1, "true", [], {}])
def test_import_target_preallocation_setter_rejects_non_boolean(import_target, value):
    with pytest.raises(TypeError):
        import_target.is_pre_allocated = value


def test_import_target_default_state(import_target):
    assert import_target.name == "json"
    assert import_target.path == "json"
    assert import_target.package is None
    assert import_target.allocated_module is None
    assert import_target.is_pre_allocated is False


def test_import_target_construct_requires_keyword_arguments(import_target_class):
    with pytest.raises(ValueError):
        import_target_class()


def test_import_target_construct_rejects_non_dictionary_kwargs(import_target_class):
    target = import_target_class(path="json")
    with pytest.raises(ValueError):
        target.construct(**{})


def test_import_target_allocate_returns_module(import_target):
    module = import_target.allocate()
    assert module is not None
    assert module.__name__ == "json"
    assert import_target.allocated_module is module


def test_import_target_allocate_caches_reference(import_target):
    first = import_target.allocate()
    second = import_target.allocate()
    assert first is second


def test_import_target_allocate_uses_relative_package(
    import_target_class,
    temporary_package,
):
    target = import_target_class(
        path=".module",
        package=temporary_package,
    )
    module = target.allocate()
    assert module.MODULE_VALUE == 456


def test_import_target_allocate_propagates_missing_module_error(import_target_class):
    target = import_target_class(
        path=f"missing_module_{uuid.uuid4().hex}",
    )
    with pytest.raises(ModuleNotFoundError):
        target.allocate()
    assert target.allocated_module is None


def test_import_target_deallocate_clears_reference(import_target):
    import_target.allocate()
    result = import_target.deallocate()
    assert result is None
    assert import_target.allocated_module is None


def test_import_target_deallocate_unallocated_target(import_target):
    assert import_target.deallocate() is None
    assert import_target.allocated_module is None


def test_import_target_deallocate_is_idempotent(import_target):
    import_target.allocate()
    assert import_target.deallocate() is None
    assert import_target.deallocate() is None


def test_import_target_deallocate_does_not_remove_sys_modules(import_target):
    module = import_target.allocate()
    import_target.deallocate()
    assert sys.modules["json"] is module


def test_import_target_pre_allocate_when_enabled(import_target_class):
    target = import_target_class(path="json", is_pre_allocated=True)
    assert target.allocated_module is not None
    assert target.allocated_module.__name__ == "json"

def test_import_target_pre_allocate_when_disabled(import_target):
    assert import_target.pre_allocate() is None
    assert import_target.allocated_module is None


def test_import_target_pre_allocate_returns_existing_module(import_target_class):
    target = import_target_class(path="json", is_pre_allocated=True)
    assert target.pre_allocate() is target.allocated_module


def test_import_target_reallocate_when_unallocated(import_target):
    module = import_target.reallocate()
    assert module is not None
    assert module.__name__ == "json"
    assert import_target.allocated_module is module


def test_import_target_reallocate_when_allocated(import_target):
    first = import_target.allocate()
    second = import_target.reallocate()
    assert second is first
    assert import_target.allocated_module is second


def test_import_target_shutdown_clears_reference(import_target):
    import_target.allocate()
    assert import_target.shutdown() is True
    assert import_target.allocated_module is None


def test_import_target_shutdown_when_unallocated(import_target):
    assert import_target.shutdown() is True
    assert import_target.allocated_module is None


def test_import_target_shutdown_is_idempotent(import_target):
    assert import_target.shutdown() is True
    assert import_target.shutdown() is True


def test_import_target_setup_accepts_nonempty_kwargs(import_target):
    assert import_target.setup(option=True) is True


def test_import_target_setup_rejects_empty_kwargs(import_target):
    with pytest.raises(ValueError):
        import_target.setup()


def test_import_target_context_manager(import_target):
    with import_target as target:
        assert target is import_target
        assert target.allocated_module is not None
    assert import_target.allocated_module is None


def test_manager_construct_initializes_empty_registry(manager):
    assert manager.import_targets == {}
    assert manager.is_pre_allocated is False


@pytest.mark.parametrize("value", [True, False])
def test_manager_preallocation_setter_accepts_boolean(manager, value):
    manager.is_pre_allocated = value
    assert manager.is_pre_allocated is value


@pytest.mark.parametrize("value", [None, 0, 1, "true", [], {}])
def test_manager_preallocation_setter_rejects_non_boolean(manager, value):
    with pytest.raises(TypeError):
        manager.is_pre_allocated = value


def test_manager_import_targets_setter_accepts_nonempty_dictionary(
    manager,
    import_target_class,
):
    target = import_target_class(path="json")
    targets = {"json": target}

    manager.import_targets = targets

    assert manager.import_targets is targets

@pytest.mark.parametrize("value", [None, {}, [], (), "targets", 123])
def test_manager_import_targets_setter_rejects_invalid_values(manager, value):
    with pytest.raises(ValueError):
        manager.import_targets = value


def test_manager_instances_have_independent_registries(manager_class):
    first = manager_class()
    second = manager_class()
    first.import_module(path="json")
    assert "json" in first.import_targets
    assert "json" not in second.import_targets


def test_manager_setup_with_empty_list(manager):
    assert manager.setup(import_targets=[]) is True
    assert manager.import_targets == {}


def test_manager_setup_with_tuple(manager):
    assert manager.setup(
        import_targets=(
            {"path": "json"},
            {"path": "platform"},
        )
    ) is True
    assert set(manager.import_targets) == {"json", "platform"}


def test_manager_setup_with_list(manager):
    assert manager.setup(
        import_targets=[
            {"path": "json"},
            {"path": "platform"},
        ]
    ) is True
    assert set(manager.import_targets) == {"json", "platform"}


def test_manager_setup_without_import_targets(manager):
    assert manager.setup(is_pre_allocated=True) is True
    assert manager.is_pre_allocated is True


def test_manager_setup_rejects_empty_kwargs(manager):
    with pytest.raises(ValueError):
        manager.setup()


@pytest.mark.parametrize("targets", [{}, "targets", 123, None])
def test_manager_setup_rejects_invalid_target_container(manager, targets):
    with pytest.raises(ValueError):
        manager.setup(import_targets=targets)


@pytest.mark.parametrize("value", [None, 0, 1, "true", [], {}])
def test_manager_setup_rejects_invalid_preallocation(manager, value):
    with pytest.raises(ValueError):
        manager.setup(import_targets=[], is_pre_allocated=value)


@pytest.mark.parametrize("target", [None, {}, [], "json", 123])
def test_manager_import_modules_rejects_invalid_target_entries(manager, target):
    with pytest.raises(ValueError):
        manager.import_modules([target])


@pytest.mark.parametrize("targets", [None, {}, "targets", 123])
def test_manager_import_modules_rejects_invalid_container(manager, targets):
    with pytest.raises(ValueError):
        manager.import_modules(targets)


def test_manager_import_modules_accepts_empty_list(manager):
    assert manager.import_modules([]) is True
    assert manager.import_targets == {}


def test_manager_import_modules_registers_multiple_targets(manager):
    assert manager.import_modules(
        [
            {"path": "json"},
            {"path": "platform"},
            {"path": "shlex"},
        ]
    ) is True
    assert set(manager.import_targets) == {"json", "platform", "shlex"}


def test_manager_import_module_requires_kwargs(manager):
    with pytest.raises(ValueError):
        manager.import_module()


@pytest.mark.parametrize("kwargs", [{"name": ""}, {"path": ""}, {"name": None, "path": None}])
def test_manager_import_module_rejects_empty_target_key(manager, kwargs):
    with pytest.raises(ValueError):
        manager.import_module(**kwargs)


@pytest.mark.parametrize("kwargs", [{"name": 123, "path": "json"}, {"path": 123}])
def test_manager_import_module_rejects_non_string_target_key(manager, kwargs):
    with pytest.raises(ValueError):
        manager.import_module(**kwargs)


def test_manager_import_module_registers_by_path(manager):
    allocation = manager.import_module(path="json")
    assert callable(allocation)
    assert "json" in manager.import_targets


def test_manager_import_module_registers_by_name(manager):
    manager.import_module(name="json_alias", path="json")
    assert "json_alias" in manager.import_targets


def test_manager_import_module_returns_bound_allocate_method(manager):
    allocation = manager.import_module(path="json")
    assert callable(allocation)
    assert allocation.__name__ == "allocate"
    assert allocation() is manager.import_targets["json"].allocated_module


def test_manager_import_module_reuses_existing_target(manager):
    first = manager.import_module(path="json")
    second = manager.import_module(path="json")
    assert first.__self__ is second.__self__
    assert len(manager.import_targets) == 1


def test_manager_import_module_reuses_existing_named_target(manager):
    first = manager.import_module(name="json_alias", path="json")
    second = manager.import_module(name="json_alias", path="platform")
    assert first.__self__ is second.__self__
    assert manager.import_targets["json_alias"].path == "json"


def test_manager_import_module_does_not_allocate_by_default(manager):
    manager.import_module(path="json")
    assert manager.import_targets["json"].allocated_module is None


def test_manager_import_module_allocates_when_enabled(manager):
    manager.is_pre_allocated = True
    manager.import_module(path="json")
    assert manager.import_targets["json"].allocated_module.__name__ == "json"


def test_manager_import_module_failed_allocation_does_not_register_invalid_target(manager):
    missing_name = f"missing_module_{uuid.uuid4().hex}"
    manager.is_pre_allocated = True
    with pytest.raises(ModuleNotFoundError):
        manager.import_module(path=missing_name)
    assert missing_name not in manager.import_targets


def test_manager_import_module_does_not_mutate_caller_kwargs(manager):
    kwargs = {"path": "json"}
    manager.import_module(**kwargs)
    assert kwargs == {"path": "json"}


def test_manager_unload_module_removes_registered_target(manager):
    manager.import_module(path="json")
    assert manager.unload_module("json") is True
    assert "json" not in manager.import_targets


def test_manager_unload_module_deallocates_target(manager):
    manager.is_pre_allocated = True
    manager.import_module(path="json")
    manager.unload_module("json")
    assert manager.import_targets == {}


@pytest.mark.parametrize("name", [None, "", 123, [], {}])
def test_manager_unload_module_rejects_invalid_name(manager, name):
    with pytest.raises(ValueError):
        manager.unload_module(name)


def test_manager_unload_module_rejects_unknown_name(manager):
    with pytest.raises(ValueError):
        manager.unload_module("unknown")


def test_manager_unload_modules_accepts_empty_list(manager):
    assert manager.unload_modules([]) is True


@pytest.mark.parametrize("names", [None, {}, "json", 123])
def test_manager_unload_modules_rejects_invalid_container(manager, names):
    with pytest.raises(ValueError):
        manager.unload_modules(names)


def test_manager_unload_modules_removes_all_targets(manager):
    manager.import_modules(
        [
            {"path": "json"},
            {"path": "platform"},
        ]
    )
    assert manager.unload_modules(["json", "platform"]) is True
    assert manager.import_targets == {}


def test_manager_unload_modules_rejects_invalid_name(manager):
    manager.import_module(path="json")
    with pytest.raises(ValueError):
        manager.unload_modules(["json", ""])


def test_manager_clear_modules_with_empty_registry(manager):
    assert manager.clear_modules() is True
    assert manager.import_targets == {}


def test_manager_clear_modules_with_registered_targets(manager):
    manager.import_modules(
        [
            {"path": "json"},
            {"path": "platform"},
        ]
    )
    assert manager.clear_modules() is True
    assert manager.import_targets == {}


def test_manager_clear_modules_deallocates_targets(manager):
    manager.is_pre_allocated = True
    manager.import_modules(
        [
            {"path": "json"},
            {"path": "platform"},
        ]
    )
    targets = tuple(manager.import_targets.values())
    assert all(target.allocated_module is not None for target in targets)
    assert manager.clear_modules() is True
    assert all(target.allocated_module is None for target in targets)


def test_manager_shutdown_clears_registry(manager):
    manager.import_modules(
        [
            {"path": "json"},
            {"path": "platform"},
        ]
    )
    assert manager.shutdown() is True
    assert manager.import_targets == {}


def test_manager_shutdown_deallocates_registered_targets(manager):
    manager.is_pre_allocated = True
    manager.import_module(path="json")
    target = manager.import_targets["json"]
    assert target.allocated_module is not None
    manager.shutdown()
    assert target.allocated_module is None


def test_manager_shutdown_is_idempotent(manager):
    assert manager.shutdown() is True
    assert manager.shutdown() is True


def test_manager_get_singleton_returns_same_instance(manager_class):
    first = manager_class.get_singleton()
    second = manager_class.get_singleton()
    assert first is second


def test_manager_get_singleton_returns_manager_instance(manager_class):
    assert isinstance(manager_class.get_singleton(), manager_class)


def test_manager_get_singleton_after_reset_returns_new_instance(manager_class):
    first = manager_class.get_singleton()
    manager_class._singleton = None
    second = manager_class.get_singleton()
    assert first is not second


def test_manager_singleton_concurrent_access(manager_class):
    instances = []
    errors = []

    def retrieve():
        try:
            instances.append(manager_class.get_singleton())
        except Exception as error:
            errors.append(error)

    threads = [threading.Thread(target=retrieve) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len(instances) == 20
    assert len({id(instance) for instance in instances}) == 1


def test_integration_register_allocate_unload(manager):
    allocation = manager.import_module(path="json")
    module = allocation()
    assert module.__name__ == "json"
    assert manager.unload_module("json") is True
    assert manager.import_targets == {}


def test_integration_multiple_modules_allocate_and_clear(manager):
    manager.import_modules(
        [
            {"path": "json"},
            {"path": "platform"},
            {"path": "shlex"},
        ]
    )
    modules = [
        manager.import_targets[name].allocate()
        for name in ("json", "platform", "shlex")
    ]
    assert [module.__name__ for module in modules] == ["json", "platform", "shlex"]
    assert manager.clear_modules() is True
    assert manager.import_targets == {}


def test_integration_two_targets_share_importlib_cache(import_target_class):
    first = import_target_class(path="json")
    second = import_target_class(path="json")
    assert first.allocate() is second.allocate()


def test_integration_deallocating_one_target_does_not_clear_another(import_target_class):
    first = import_target_class(path="json")
    second = import_target_class(path="json")
    first.allocate()
    second.allocate()
    first.deallocate()
    assert first.allocated_module is None
    assert second.allocated_module is not None


def test_integration_manager_registry_isolated_between_instances(manager_class):
    first = manager_class()
    second = manager_class()
    first.import_module(path="json")
    second.import_module(path="platform")
    assert set(first.import_targets) == {"json"}
    assert set(second.import_targets) == {"platform"}


def test_integration_temporary_module_import(import_target_class, temporary_module):
    target = import_target_class(path=temporary_module)
    module = target.allocate()
    assert module.VALUE == 123


def test_integration_temporary_module_import_through_manager(manager, temporary_module):
    allocation = manager.import_module(path=temporary_module)
    assert allocation().VALUE == 123


def test_integration_relative_package_import_through_manager(
    manager,
    temporary_package,
):
    allocation = manager.import_module(
        name="temporary_relative_module",
        path=".module",
        package=temporary_package,
    )
    assert allocation().MODULE_VALUE == 456


def test_integration_failed_import_can_be_retried(import_target_class, tmp_path, monkeypatch):
    module_name = f"retry_module_{uuid.uuid4().hex}"
    target = import_target_class(path=module_name)

    with pytest.raises(ModuleNotFoundError):
        target.allocate()

    module_path = tmp_path / f"{module_name}.py"
    module_path.write_text("VALUE = 789\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()

    module = target.allocate()
    assert module.VALUE == 789
    sys.modules.pop(module_name, None)


def test_integration_manager_import_failure_during_lazy_allocation(manager):
    module_name = f"missing_module_{uuid.uuid4().hex}"
    allocation = manager.import_module(path=module_name)
    assert module_name in manager.import_targets
    with pytest.raises(ModuleNotFoundError):
        allocation()


def test_integration_manager_setup_with_preallocation(manager):
    assert manager.setup(
        import_targets=[
            {"path": "json"},
            {"path": "platform"},
        ],
        is_pre_allocated=True,
    ) is True
    assert all(
        target.allocated_module is not None
        for target in manager.import_targets.values()
    )


def test_integration_manager_setup_failure_state(manager):
    manager.import_module(path="json")
    original_targets = dict(manager.import_targets)

    with pytest.raises(ValueError):
        manager.setup(
            import_targets=[{"path": "platform"}, None],
        )

    assert manager.import_targets == original_targets


def test_integration_manager_import_failure_state(manager):
    manager.is_pre_allocated = True
    module_name = f"missing_module_{uuid.uuid4().hex}"

    with pytest.raises(ModuleNotFoundError):
        manager.import_modules(
            [
                {"path": "json"},
                {"path": module_name},
            ]
        )

    assert module_name not in manager.import_targets


def test_integration_manager_duplicate_paths_with_different_names(manager):
    first = manager.import_module(name="first_alias", path="json")
    second = manager.import_module(name="second_alias", path="json")
    assert first.__self__ is not second.__self__
    assert set(manager.import_targets) == {"first_alias", "second_alias"}
    assert first() is second()


def test_integration_manager_same_name_different_paths_preserves_first(manager):
    first = manager.import_module(name="shared_alias", path="json")
    second = manager.import_module(name="shared_alias", path="platform")
    assert first.__self__ is second.__self__
    assert manager.import_targets["shared_alias"].path == "json"


def test_integration_manager_unload_does_not_remove_sys_modules(manager):
    module = manager.import_module(path="json")()
    manager.unload_module("json")
    assert sys.modules["json"] is module


def test_integration_import_target_reallocate_preserves_importlib_cache(import_target):
    first = import_target.allocate()
    import_target.deallocate()
    second = import_target.reallocate()
    assert second is first


def test_integration_importlib_spec_for_json():
    assert importlib.util.find_spec("json") is not None

@pytest.mark.parametrize(
    "value",
    [None, 0, 1, "true", [], {}],
)
def test_import_target_construct_rejects_invalid_preallocation(
    import_target_class,
    value,
):
    with pytest.raises(ValueError):
        import_target_class(
            path="json",
            is_pre_allocated=value,
        )


def test_import_target_construct_accepts_custom_name_and_package(
    import_target_class,
    temporary_package,
):
    target = import_target_class(
        name="custom_module",
        path=".module",
        package=temporary_package,
    )

    assert target.name == "custom_module"
    assert target.path == ".module"
    assert target.package == temporary_package


def test_import_target_allocate_after_shutdown(import_target):
    import_target.allocate()
    import_target.shutdown()

    module = import_target.allocate()

    assert module is not None
    assert import_target.allocated_module is module


def test_import_target_reallocate_after_failed_allocation(
    import_target_class,
    tmp_path,
    monkeypatch,
):
    module_name = f"retry_module_{uuid.uuid4().hex}"
    target = import_target_class(path=module_name)

    with pytest.raises(ModuleNotFoundError):
        target.allocate()

    module_path = tmp_path / f"{module_name}.py"
    module_path.write_text("VALUE = 789\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()

    module = target.reallocate()

    assert module.VALUE == 789
    assert target.allocated_module is module

    sys.modules.pop(module_name, None)


def test_import_target_shutdown_after_failed_allocation(
    import_target_class,
):
    target = import_target_class(
        path=f"missing_module_{uuid.uuid4().hex}",
    )

    with pytest.raises(ModuleNotFoundError):
        target.allocate()

    assert target.shutdown() is True
    assert target.allocated_module is None


def test_import_target_context_manager_cleans_up_after_exception(
    import_target,
):
    with pytest.raises(RuntimeError):
        with import_target as target:
            assert target.allocated_module is not None
            raise RuntimeError("test")

    assert import_target.allocated_module is None


def test_import_target_context_manager_repeated_entry(import_target):
    with import_target as first:
        first_module = first.allocated_module

    assert import_target.allocated_module is None

    with import_target as second:
        assert second is import_target
        assert second.allocated_module is first_module

    assert import_target.allocated_module is None


def test_import_target_context_manager_propagates_allocation_error(
    import_target_class,
):
    target = import_target_class(
        path=f"missing_module_{uuid.uuid4().hex}",
    )

    with pytest.raises(ModuleNotFoundError):
        with target:
            pass

    assert target.allocated_module is None


def test_manager_setup_duplicate_paths(manager):
    assert manager.setup(
        import_targets=[
            {"path": "json"},
            {"path": "json"},
        ],
    ) is True

    assert list(manager.import_targets) == ["json"]
    assert manager.import_targets["json"].path == "json"


def test_manager_setup_duplicate_names_preserves_first(manager):
    assert manager.setup(
        import_targets=[
            {"name": "shared", "path": "json"},
            {"name": "shared", "path": "platform"},
        ],
    ) is True

    assert list(manager.import_targets) == ["shared"]
    assert manager.import_targets["shared"].path == "json"


def test_manager_setup_existing_name_preserves_existing_target(manager):
    manager.import_module(name="shared", path="json")
    original = manager.import_targets["shared"]

    manager.setup(
        import_targets=[
            {"name": "shared", "path": "platform"},
            {"path": "shlex"},
        ],
    )

    assert manager.import_targets["shared"] is original
    assert manager.import_targets["shared"].path == "json"
    assert "shlex" in manager.import_targets


def test_manager_setup_disables_preallocation_after_enabling(manager):
    manager.setup(
        import_targets=[{"path": "json"}],
        is_pre_allocated=True,
    )

    assert manager.is_pre_allocated is True
    assert manager.import_targets["json"].allocated_module is not None

    manager.setup(
        import_targets=[],
        is_pre_allocated=False,
    )

    assert manager.is_pre_allocated is False


def test_manager_setup_repeated_calls_preserve_existing_targets(manager):
    manager.setup(
        import_targets=[
            {"path": "json"},
        ],
    )

    original = manager.import_targets["json"]

    manager.setup(
        import_targets=[
            {"path": "platform"},
        ],
    )

    assert manager.import_targets["json"] is original
    assert set(manager.import_targets) == {"json", "platform"}


def test_manager_setup_empty_list_preserves_existing_targets(manager):
    manager.import_module(path="json")
    original = manager.import_targets["json"]

    assert manager.setup(import_targets=[]) is True

    assert manager.import_targets["json"] is original


def test_manager_setup_allocation_failure_preserves_registry(manager):
    manager.import_module(path="shlex")
    original_targets = dict(manager.import_targets)

    missing_name = f"missing_module_{uuid.uuid4().hex}"

    with pytest.raises(ModuleNotFoundError):
        manager.setup(
            import_targets=[
                {"path": "platform"},
                {"path": missing_name},
            ],
            is_pre_allocated=True,
        )

    assert manager.import_targets == original_targets
    assert manager.is_pre_allocated is False


def test_manager_setup_allocation_failure_deallocates_staged_targets(
    manager,
):
    missing_name = f"missing_module_{uuid.uuid4().hex}"

    with pytest.raises(ModuleNotFoundError):
        manager.setup(
            import_targets=[
                {"path": "platform"},
                {"path": missing_name},
            ],
            is_pre_allocated=True,
        )

    assert manager.import_targets == {}


def test_manager_setup_invalid_target_preserves_preallocation_state(
    manager,
):
    manager.is_pre_allocated = False

    with pytest.raises(ValueError):
        manager.setup(
            import_targets=[None],
            is_pre_allocated=True,
        )

    assert manager.is_pre_allocated is False


def test_manager_import_modules_failure_preserves_prior_registrations(
    manager,
):
    manager.import_module(path="shlex")
    original = manager.import_targets["shlex"]

    manager.is_pre_allocated = True
    missing_name = f"missing_module_{uuid.uuid4().hex}"

    with pytest.raises(ModuleNotFoundError):
        manager.import_modules(
            [
                {"path": "json"},
                {"path": missing_name},
            ]
        )

    assert manager.import_targets["shlex"] is original
    assert "json" in manager.import_targets
    assert missing_name not in manager.import_targets


def test_manager_import_modules_duplicate_paths(manager):
    assert manager.import_modules(
        [
            {"path": "json"},
            {"path": "json"},
        ]
    ) is True

    assert list(manager.import_targets) == ["json"]


def test_manager_import_modules_duplicate_names_preserves_first(manager):
    assert manager.import_modules(
        [
            {"name": "shared", "path": "json"},
            {"name": "shared", "path": "platform"},
        ]
    ) is True

    assert manager.import_targets["shared"].path == "json"


def test_manager_import_modules_preserves_existing_target(manager):
    manager.import_module(name="shared", path="json")
    original = manager.import_targets["shared"]

    manager.import_modules(
        [
            {"name": "shared", "path": "platform"},
        ]
    )

    assert manager.import_targets["shared"] is original
    assert manager.import_targets["shared"].path == "json"


def test_manager_unload_module_deallocates_allocated_target(manager):
    manager.is_pre_allocated = True
    manager.import_module(path="json")

    target = manager.import_targets["json"]
    assert target.allocated_module is not None

    assert manager.unload_module("json") is True

    assert target.allocated_module is None
    assert "json" not in manager.import_targets


def test_manager_unload_modules_rejects_duplicate_names(manager):
    manager.import_module(path="json")

    with pytest.raises(ValueError):
        manager.unload_modules(["json", "json"])


def test_manager_clear_modules_after_partial_registration(manager):
    manager.import_module(path="json")
    manager.import_module(path="platform")

    assert manager.clear_modules() is True
    assert manager.import_targets == {}


def test_manager_shutdown_after_failed_setup(manager):
    missing_name = f"missing_module_{uuid.uuid4().hex}"

    with pytest.raises(ModuleNotFoundError):
        manager.setup(
            import_targets=[
                {"path": "platform"},
                {"path": missing_name},
            ],
            is_pre_allocated=True,
        )

    assert manager.shutdown() is True
    assert manager.import_targets == {}


def test_manager_import_targets_setter_rejects_invalid_keys(manager):
    for targets in (
        {"": object()},
        {None: object()},
        {123: object()},
    ):
        with pytest.raises(ValueError):
            manager.import_targets = targets


def test_manager_import_targets_setter_rejects_invalid_target_values(
    manager,
):
    with pytest.raises(ValueError):
        manager.import_targets = {"json": object()}


def test_manager_import_targets_setter_rejects_empty_target_dictionary(
    manager,
):
    with pytest.raises(ValueError):
        manager.import_targets = {}


def test_manager_singleton_concurrent_access_with_barrier(manager_class):
    barrier = threading.Barrier(20)
    lock = threading.Lock()
    instances = []
    errors = []

    def retrieve():
        try:
            barrier.wait()
            instance = manager_class.get_singleton()

            with lock:
                instances.append(instance)
        except Exception as error:
            with lock:
                errors.append(error)

    threads = [
        threading.Thread(target=retrieve)
        for _ in range(20)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert errors == []
    assert len(instances) == 20
    assert len({id(instance) for instance in instances}) == 1


def test_integration_import_target_path_change_after_allocation(
    import_target,
):
    import_target.allocate()

    import_target.path = "platform"

    module = import_target.allocate()

    assert module.__name__ == "json"


def test_integration_import_target_name_change_after_allocation(
    import_target,
):
    module = import_target.allocate()

    import_target.name = "renamed"

    assert import_target.allocate() is module
    assert import_target.name == "renamed"


def test_integration_import_target_package_change_after_allocation(
    import_target,
):
    module = import_target.allocate()

    import_target.package = "custom_package"

    assert import_target.allocate() is module


def test_integration_manager_unload_and_reregister_target(manager):
    first = manager.import_module(path="json")
    first_module = first()

    manager.unload_module("json")

    second = manager.import_module(path="json")
    second_module = second()

    assert second_module is first_module
    assert manager.import_targets["json"].allocated_module is second_module


def test_integration_manager_duplicate_aliases_share_module(manager):
    first = manager.import_module(name="first_alias", path="json")
    second = manager.import_module(name="second_alias", path="json")

    assert first.__self__ is not second.__self__
    assert first() is second()


def test_integration_manager_preallocation_with_duplicate_paths(manager):
    manager.setup(
        import_targets=[
            {"path": "json"},
            {"name": "json_alias", "path": "json"},
        ],
        is_pre_allocated=True,
    )

    first = manager.import_targets["json"]
    second = manager.import_targets["json_alias"]

    assert first.allocated_module is not None
    assert second.allocated_module is not None
    assert first.allocated_module is second.allocated_module


def test_integration_nested_package_import(import_target_class, tmp_path, monkeypatch):
    package_name = f"nested_package_{uuid.uuid4().hex}"
    package_path = tmp_path / package_name
    nested_path = package_path / "nested"

    nested_path.mkdir(parents=True)

    (package_path / "__init__.py").write_text(
        "PACKAGE_VALUE = 1\n",
        encoding="utf-8",
    )
    (nested_path / "__init__.py").write_text(
        "NESTED_VALUE = 2\n",
        encoding="utf-8",
    )
    (nested_path / "module.py").write_text(
        "VALUE = 3\n",
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()

    try:
        target = import_target_class(
            path=f"{package_name}.nested.module",
        )

        module = target.allocate()

        assert module.VALUE == 3
    finally:
        for name in tuple(sys.modules):
            if name == package_name or name.startswith(f"{package_name}."):
                sys.modules.pop(name, None)


def test_integration_import_target_internal_import_error(import_target_class, tmp_path, monkeypatch):
    module_name = f"broken_module_{uuid.uuid4().hex}"
    module_path = tmp_path / f"{module_name}.py"

    module_path.write_text(
        "raise RuntimeError('module initialization failed')\n",
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()

    target = import_target_class(path=module_name)

    with pytest.raises(RuntimeError, match="module initialization failed"):
        target.allocate()

    assert target.allocated_module is None
    assert module_name not in sys.modules


def test_integration_import_target_missing_spec(import_target_class):
    target = import_target_class(
        path=f"missing_module_{uuid.uuid4().hex}",
    )

    assert importlib.util.find_spec(target.path) is None

    with pytest.raises(ModuleNotFoundError):
        target.allocate()

    assert target.allocated_module is None


def test_integration_manager_failed_import_can_be_retried(
    manager,
    tmp_path,
    monkeypatch,
):
    module_name = f"manager_retry_module_{uuid.uuid4().hex}"
    allocation = manager.import_module(path=module_name)

    with pytest.raises(ModuleNotFoundError):
        allocation()

    module_path = tmp_path / f"{module_name}.py"
    module_path.write_text("VALUE = 987\n", encoding="utf-8")

    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()

    module = allocation()

    assert module.VALUE == 987
    assert manager.import_targets[module_name].allocated_module is module

    sys.modules.pop(module_name, None)


def test_integration_manager_shutdown_after_allocation_failure(manager):
    module_name = f"missing_module_{uuid.uuid4().hex}"
    allocation = manager.import_module(path=module_name)

    with pytest.raises(ModuleNotFoundError):
        allocation()

    assert manager.shutdown() is True
    assert manager.import_targets == {}
def test_import_target_deallocate_returns_none_when_unallocated(
    import_target,
):
    assert import_target.allocated_module is None
    assert import_target.deallocate() is None


def test_manager_setup_existing_target_deallocates_duplicate(
    manager,
):
    manager.is_pre_allocated = True

    manager.import_module(name="shared", path="json")
    existing = manager.import_targets["shared"]
    existing_module = existing.allocated_module

    assert existing_module is not None

    assert manager.setup(
        import_targets=[
            {"name": "shared", "path": "platform"},
        ],
        is_pre_allocated=True,
    ) is True

    assert manager.import_targets["shared"] is existing
    assert manager.import_targets["shared"].path == "json"
    assert existing.allocated_module is existing_module


def test_manager_setup_rolls_back_allocated_staged_targets(
    manager,
    module_under_test,
    monkeypatch,
):
    original_import_target = module_under_test._ImportTarget
    allocated_targets = []

    class TrackingImportTarget(original_import_target):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            allocated_targets.append(self)

    def construct_target(**kwargs):
        if kwargs["path"] == "invalid_target":
            raise ValueError("invalid target")

        return TrackingImportTarget(**kwargs)

    monkeypatch.setattr(
        module_under_test,
        "_ImportTarget",
        construct_target,
    )

    with pytest.raises(ValueError, match="invalid target"):
        manager.setup(
            import_targets=[
                {"path": "json"},
                {"path": "invalid_target"},
            ],
            is_pre_allocated=True,
        )

    assert manager.import_targets == {}
    assert len(allocated_targets) == 1
    assert allocated_targets[0].allocated_module is None


def test_manager_context_manager_returns_manager(manager):
    with manager as target:
        assert target is manager


def test_manager_context_manager_clears_registry(manager):
    manager.import_module(path="json")

    with manager as target:
        assert target.import_targets

    assert manager.import_targets == {}


def test_manager_context_manager_deallocates_targets(manager):
    manager.is_pre_allocated = True
    manager.import_module(path="json")

    target = manager.import_targets["json"]

    assert target.allocated_module is not None

    with manager:
        pass

    assert target.allocated_module is None
    assert manager.import_targets == {}


def test_manager_context_manager_cleans_up_after_exception(manager):
    manager.import_module(path="json")

    with pytest.raises(RuntimeError, match="test"):
        with manager:
            raise RuntimeError("test")

    assert manager.import_targets == {}


def test_manager_import_module_rejects_missing_import_target(
    manager,
    module_under_test,
    monkeypatch,
):
    monkeypatch.setattr(
        module_under_test,
        "_ImportTarget",
        lambda **kwargs: None,
    )

    with pytest.raises(ValueError, match="import_target"):
        manager.import_module(path="json")

    assert manager.import_targets == {}


def test_manager_clear_modules_returns_true_when_registry_is_empty(
    manager,
):
    assert manager.import_targets == {}
    assert manager.clear_modules() is True
    assert manager.import_targets == {}

def test_import_target_allocated_module_getter_returns_none(
    import_target_class,
):
    target = import_target_class(path="json")

    assert target.allocated_module is None


def test_import_target_allocated_module_getter_returns_assigned_value(
    import_target_class,
):
    target = import_target_class(path="json")
    module = object()

    target.allocated_module = module

    assert target.allocated_module is module


def test_import_target_allocated_module_setter_accepts_none(
    import_target_class,
):
    target = import_target_class(path="json")
    target.allocated_module = object()

    target.allocated_module = None

    assert target.allocated_module is None


def test_import_target_allocated_module_setter_accepts_arbitrary_value(
    import_target_class,
):
    target = import_target_class(path="json")
    value = object()

    target.allocated_module = value

    assert target.allocated_module is value


@pytest.mark.parametrize("value", [True, False])
def test_import_target_member_callable_setter_accepts_boolean(
    import_target,
    value,
):
    import_target.is_member_callable = value

    assert import_target.is_member_callable is value


@pytest.mark.parametrize("value", [None, 0, 1, "true", [], {}])
def test_import_target_member_callable_setter_rejects_non_boolean(
    import_target,
    value,
):
    with pytest.raises(ValueError):
        import_target.is_member_callable = value


def test_import_target_member_setter_accepts_valid_values(
    import_target,
):
    for value in (None, "", "loads", "utilities.handler"):
        import_target.member = value

        assert import_target.member == (value or None)


@pytest.mark.parametrize("value", [123, [], {}, True])
def test_import_target_member_setter_rejects_invalid_values(
    import_target,
    value,
):
    with pytest.raises(TypeError):
        import_target.member = value


def test_import_target_member_constructor_accepts_none(
    import_target_class,
):
    target = import_target_class(
        path="json",
        member=None,
    )

    assert target.member is None


def test_import_target_member_constructor_accepts_empty_string(
    import_target_class,
):
    target = import_target_class(
        path="json",
        member="",
    )

    assert target.member == ""


@pytest.mark.parametrize("value", [123, [], {}, True])
def test_import_target_member_constructor_rejects_invalid_values(
    import_target_class,
    value,
):
    with pytest.raises(TypeError):
        import_target_class(
            path="json",
            member=value,
        )


def test_import_target_callable_member_allocation(
    import_target_class,
):
    target = import_target_class(
        path="json",
        member="JSONDecoder",
        is_member_callable=True,
    )

    result = target.allocate()

    assert isinstance(result, importlib.import_module("json").JSONDecoder)
    assert target.allocated_module is result


def test_import_target_nested_member_allocation(
    import_target_class,
):
    target = import_target_class(
        path="json",
        member="decoder.JSONDecoder",
    )

    result = target.allocate()

    assert result is importlib.import_module("json").decoder.JSONDecoder


def test_import_target_callable_member_setter_updates_state(
    import_target,
):
    import_target.is_member_callable = True

    assert import_target.is_member_callable is True
    assert import_target.path == "json"


def test_import_target_setup_with_multiple_kwargs(
    import_target,
):
    assert import_target.setup(
        option=True,
        another_option="value",
    ) is True


def test_import_target_setup_rejects_empty_kwargs(
    import_target,
):
    with pytest.raises(ValueError):
        import_target.setup()


def test_manager_setup_with_only_preallocation_argument(
    manager,
):
    assert manager.setup(is_pre_allocated=True) is True

    assert manager.is_pre_allocated is True
    assert manager.import_targets == {}


def test_manager_setup_preserves_preallocation_when_omitted(
    manager,
):
    manager.is_pre_allocated = True

    assert manager.setup(import_targets=[]) is True

    assert manager.is_pre_allocated is True


def test_manager_import_module_rejects_empty_name_and_path(
    manager,
):
    with pytest.raises(ValueError):
        manager.import_module(name="", path="")

    assert manager.import_targets == {}


def test_manager_import_module_uses_path_when_name_is_absent(
    manager,
):
    allocation = manager.import_module(path="json")

    assert callable(allocation)
    assert "json" in manager.import_targets


def test_manager_import_module_uses_name_when_provided(
    manager,
):
    allocation = manager.import_module(
        name="json_alias",
        path="json",
    )

    assert callable(allocation)
    assert "json_alias" in manager.import_targets


def test_manager_import_module_rejects_undefined_target(
    manager,
    module_under_test,
    monkeypatch,
):
    monkeypatch.setattr(
        module_under_test,
        "_ImportTarget",
        lambda **kwargs: None,
    )

    with pytest.raises(ValueError, match="import_target"):
        manager.import_module(path="json")

    assert manager.import_targets == {}


def test_manager_import_module_returns_allocate_method(
    manager,
):
    allocation = manager.import_module(path="json")

    assert callable(allocation)
    assert allocation.__name__ == "allocate"

    module = allocation()

    assert module.__name__ == "json"


def test_manager_import_module_reuses_registered_target(
    manager,
):
    first = manager.import_module(path="json")
    target = manager.import_targets["json"]

    second = manager.import_module(path="json")

    assert manager.import_targets["json"] is target
    assert first.__self__ is second.__self__


def test_manager_import_module_with_callable_member(
    manager,
):
    allocation = manager.import_module(
        name="json_decoder",
        path="json",
        member="JSONDecoder",
        is_member_callable=True,
    )

    result = allocation()

    assert isinstance(result, importlib.import_module("json").JSONDecoder)


def test_manager_import_module_with_nested_member(
    manager,
):
    allocation = manager.import_module(
        name="json_decoder",
        path="json",
        member="decoder.JSONDecoder",
    )

    assert allocation() is importlib.import_module("json").decoder.JSONDecoder


def test_manager_import_module_with_relative_package(
    manager,
    temporary_package,
):
    allocation = manager.import_module(
        name="relative_module",
        path=".module",
        package=temporary_package,
    )

    assert allocation().MODULE_VALUE == 456


def test_manager_import_modules_with_empty_list(
    manager,
):
    assert manager.import_modules([]) is True
    assert manager.import_targets == {}


def test_manager_unload_modules_with_empty_list(
    manager,
):
    assert manager.unload_modules([]) is True
    assert manager.import_targets == {}


def test_manager_clear_modules_after_multiple_registrations(
    manager,
):
    manager.import_modules(
        [
            {"path": "json"},
            {"path": "platform"},
        ]
    )

    assert manager.clear_modules() is True
    assert manager.import_targets == {}


def test_import_target_member_callable_constructor_state(
    import_target_class,
):
    target = import_target_class(
        path="json",
        member="JSONDecoder",
        is_member_callable=True,
    )

    assert target.is_member_callable is True
    assert target.member == "JSONDecoder"


def test_import_target_member_callable_allocation_with_nested_member(
    import_target_class,
):
    target = import_target_class(
        path="json",
        member="decoder.JSONDecoder",
        is_member_callable=True,
    )

    result = target.allocate()

    assert isinstance(result, importlib.import_module("json").JSONDecoder)


def test_import_target_allocate_with_empty_member_segments(
    import_target_class,
):
    target = import_target_class(
        path="json",
        member=".decoder..JSONDecoder.",
    )

    assert target.allocate() is importlib.import_module("json").decoder.JSONDecoder
    
def test_import_target_construct_defaults_is_member_callable(
    import_target_class,
):
    target = import_target_class(path="json")

    assert target.is_member_callable is False


@pytest.mark.parametrize("value", [True, False])
def test_import_target_construct_accepts_is_member_callable_boolean(
    import_target_class,
    value,
):
    target = import_target_class(
        path="json",
        is_member_callable=value,
    )

    assert target.is_member_callable is value


@pytest.mark.parametrize(
    "value",
    [None, 0, 1, "true", "false", [], {}, ()],
)
def test_import_target_construct_rejects_invalid_is_member_callable(
    import_target_class,
    value,
):
    with pytest.raises(
        ValueError,
        match="kwargs.is_member_callable",
    ):
        import_target_class(
            path="json",
            is_member_callable=value,
        )