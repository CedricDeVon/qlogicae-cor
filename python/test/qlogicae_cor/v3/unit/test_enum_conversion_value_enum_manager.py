
import pytest

from qlogicae_cor.v3.library.enum_conversion_value import (
    EnumConversionValue,
)

from qlogicae_cor.v3.library.enum_conversion_value_enum_manager import (
    EnumConversionValueEnumManager,
)

import importlib

from enum import StrEnum

from qlogicae_cor.v3.library import external_dependency_manager


@pytest.fixture
def manager_class():
    manager_type = EnumConversionValueEnumManager()
    manager_type._singleton = None

    yield manager_type

    manager_type._singleton = None


@pytest.fixture
def manager(manager_class):
    return manager_class.get_singleton()


class EnumConversionValueEnumManagerTest:
    def test_should_return_class_when_factory_is_called(self):
        result = EnumConversionValueEnumManager()

        assert isinstance(result, type)

    def test_should_return_same_class_when_factory_is_called_repeatedly(
        self,
    ):
        first_result = EnumConversionValueEnumManager()
        second_result = EnumConversionValueEnumManager()

        assert first_result is second_result

    def test_should_initialize_singleton_when_requested(
        self,
        manager_class,
    ):
        result = manager_class.get_singleton()

        assert isinstance(result, manager_class)

    def test_should_return_same_instance_when_singleton_is_requested(
        self,
        manager_class,
    ):
        first_result = manager_class.get_singleton()
        second_result = manager_class.get_singleton()

        assert first_result is second_result

    def test_should_initialize_dependencies_when_construct_is_called(
        self,
        manager,
    ):
        result = manager.construct()

        assert result is True

    def test_should_return_true_when_setup_receives_arguments(
        self,
        manager,
    ):
        result = manager.setup(enabled=True)

        assert result is True

    def test_should_return_false_when_setup_receives_empty_arguments(
        self,
        manager,
    ):
        result = manager.setup()

        assert result is False

    def test_should_return_true_when_shutdown_is_called(
        self,
        manager,
    ):
        result = manager.shutdown()

        assert result is True

    def test_should_return_self_when_context_manager_is_entered(
        self,
        manager_class,
    ):
        instance = manager_class()

        with instance as result:
            assert result is instance

    def test_should_shutdown_when_context_manager_exits(
        self,
        manager_class,
        monkeypatch,
    ):
        shutdown_calls = []

        def shutdown(instance):
            shutdown_calls.append(instance)
            return True

        monkeypatch.setattr(
            manager_class,
            "shutdown",
            shutdown,
        )

        with manager_class() as instance:
            assert isinstance(instance, manager_class)

        assert shutdown_calls == [instance]

    def test_should_shutdown_when_context_manager_exits_with_exception(
        self,
        manager_class,
        monkeypatch,
    ):
        shutdown_calls = []

        def shutdown(instance):
            shutdown_calls.append(instance)
            return True

        monkeypatch.setattr(
            manager_class,
            "shutdown",
            shutdown,
        )

        with pytest.raises(RuntimeError):
            with manager_class():
                raise RuntimeError("execution failed")

        assert len(shutdown_calls) == 1

    @pytest.mark.parametrize(
        ("input_type", "expected_value"),
        [
            pytest.param(
                EnumConversionValue().STRING,
                "string",
                id="string",
            ),
            pytest.param(
                EnumConversionValue().ENUM,
                "enum",
                id="enum",
            ),
            pytest.param(
                EnumConversionValue().CUSTOM,
                "custom",
                id="custom",
            ),
            pytest.param(
                EnumConversionValue().NONE,
                "none",
                id="none",
            ),
            pytest.param(
                "invalid",
                "none",
                id="invalid",
            ),
            pytest.param(
                100,
                "none",
                id="integer",
            ),
        ],
    )
    def test_should_convert_input_to_string_when_output_is_string(
        self,
        manager,
        input_type,
        expected_value,
    ):
        result = manager.convert_value(
            input_type,
            EnumConversionValue().STRING,
        )

        assert result == expected_value

    def test_should_convert_input_to_string_when_output_is_omitted(
        self,
        manager,
    ):
        result = manager.convert_value(
            EnumConversionValue().STRING,
        )

        assert result == "string"

    def test_should_convert_none_input_to_string_when_output_is_omitted(
        self,
        manager,
    ):
        result = manager.convert_value(None)

        assert result == "none"

    @pytest.mark.parametrize(
        ("input_type", "expected_value"),
        [
            pytest.param(
                "string",
                EnumConversionValue().STRING,
                id="string",
            ),
            pytest.param(
                "none",
                EnumConversionValue().ENUM,
                id="none",
            ),
            pytest.param(
                "custom",
                EnumConversionValue().CUSTOM,
                id="custom",
            ),
            pytest.param(
                "STRING",
                EnumConversionValue().STRING,
                id="uppercase-string",
            ),
            pytest.param(
                "CUSTOM",
                EnumConversionValue().CUSTOM,
                id="uppercase-custom",
            ),
            pytest.param(
                "invalid",
                EnumConversionValue().NONE,
                id="invalid",
            ),
            pytest.param(
                "",
                EnumConversionValue().NONE,
                id="empty-string",
            ),
        ],
    )
    def test_should_convert_input_to_enum_when_output_is_enum(
        self,
        manager,
        input_type,
        expected_value,
    ):
        result = manager.convert_value(
            input_type,
            EnumConversionValue().ENUM,
        )

        assert result == expected_value

    @pytest.mark.parametrize(
        "output_type",
        [
            pytest.param(
                EnumConversionValue().CUSTOM,
                id="custom",
            ),
            pytest.param(
                EnumConversionValue().NONE,
                id="none",
            ),
            pytest.param(
                "invalid",
                id="invalid",
            ),
            pytest.param(
                100,
                id="integer",
            ),
        ],
    )
    def test_should_return_none_when_output_type_is_unsupported(
        self,
        manager,
        output_type,
    ):
        result = manager.convert_value(
            EnumConversionValue().STRING,
            output_type,
        )

        assert result == EnumConversionValue().NONE

    def test_should_return_none_when_input_is_invalid_for_enum_conversion(
        self,
        manager,
    ):
        result = manager.convert_value(
            None,
            EnumConversionValue().ENUM,
        )

        assert result == EnumConversionValue().NONE

    def test_should_return_none_when_input_is_empty_for_enum_conversion(
        self,
        manager,
    ):
        result = manager.convert_value(
            "",
            EnumConversionValue().ENUM,
        )

        assert result == EnumConversionValue().NONE

    def test_should_preserve_singleton_after_repeated_shutdown(
        self,
        manager_class,
    ):
        instance = manager_class.get_singleton()

        first_result = instance.shutdown()
        second_result = instance.shutdown()

        assert first_result is True
        assert second_result is True
        assert manager_class.get_singleton() is instance

    def test_should_preserve_functionality_after_shutdown(
        self,
        manager,
    ):
        manager.shutdown()

        result = manager.convert_value(
            EnumConversionValue().ENUM,
            EnumConversionValue().STRING,
        )

        assert result == "enum"

    def test_should_complete_repeated_conversions_without_state_corruption(
        self,
        manager,
    ):
        expected_values = (
            "string",
            "enum",
            "custom",
            "none",
        )

        for iteration in range(1000):
            input_type = (
                EnumConversionValue().STRING,
                EnumConversionValue().ENUM,
                EnumConversionValue().CUSTOM,
                EnumConversionValue().NONE,
            )[iteration % 4]

            result = manager.convert_value(input_type)

            assert result == expected_values[iteration % 4]

    def test_should_complete_repeated_construction_and_shutdown(
        self,
        manager_class,
    ):
        for _ in range(100):
            instance = manager_class()

            assert instance.shutdown() is True

@pytest.fixture
def module():
    return importlib.reload(
        external_dependency_manager
    )


@pytest.fixture
def target_class(module):
    module.ExternalDependencyManager()

    return module._ImportTarget


@pytest.fixture
def manager_class(module):
    return module.ExternalDependencyManager()


@pytest.fixture
def manager(manager_class):
    return manager_class()


@pytest.fixture
def target_kwargs():
    return {
        "path": "math",
    }


@pytest.fixture
def target(target_class, target_kwargs):
    return target_class(**target_kwargs)


class ImportTargetTest:

    def test_should_return_class_when_manager_is_allocated(
        self,
        module,
    ):
        module.ExternalDependencyManager()

        assert isinstance(module._ImportTarget, type)

    def test_should_initialize_target_when_construct_is_called(
        self,
        target,
    ):
        assert target.path == "math"
        assert target.name == "math"
        assert target.package is None
        assert target.member == ""
        assert target.allocated_module is None
        assert target.is_pre_allocated is False
        assert target.is_member_callable is False

    def test_should_return_true_when_construct_receives_valid_arguments(
        self,
        target_class,
    ):
        target = target_class(path="math")

        assert target.construct(path="math") is True

    def test_should_raise_value_error_when_construct_receives_empty_arguments(
        self,
        target_class,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.*non-empty dictionary",
        ):
            target_class()

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="empty-string"),
            pytest.param(100, id="integer"),
            pytest.param((), id="tuple"),
        ],
    )
    def test_should_raise_value_error_when_construct_path_is_invalid(
        self,
        target_class,
        path,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.path",
        ):
            target_class(path=path)

    def test_should_raise_value_error_when_construct_name_is_not_string(
        self,
        target_class,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.name",
        ):
            target_class(path="math", name=100)

    def test_should_use_path_as_name_when_name_is_omitted(
        self,
        target_class,
    ):
        target = target_class(path="math")

        assert target.name == "math"

    def test_should_use_path_as_name_when_name_is_empty(
        self,
        target_class,
    ):
        target = target_class(path="math", name="")

        assert target.name == "math"

    def test_should_raise_type_error_when_construct_package_is_invalid(
        self,
        target_class,
    ):
        with pytest.raises(
            TypeError,
            match="kwargs.package",
        ):
            target_class(path="math", package=100)

    def test_should_normalize_empty_package_to_none(
        self,
        target_class,
    ):
        target = target_class(path="math", package="")

        assert target.package is None

    def test_should_raise_type_error_when_construct_member_is_invalid(
        self,
        target_class,
    ):
        with pytest.raises(
            TypeError,
            match="kwargs.member",
        ):
            target_class(path="math", member=100)

    def test_should_preserve_none_member_when_construct_receives_none(
        self,
        target_class,
    ):
        target = target_class(path="math", member=None)

        assert target.member is None

    def test_should_raise_value_error_when_pre_allocation_is_invalid(
        self,
        target_class,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.is_pre_allocated",
        ):
            target_class(
                path="math",
                is_pre_allocated="true",
            )

    def test_should_raise_value_error_when_callable_flag_is_invalid(
        self,
        target_class,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.is_member_callable",
        ):
            target_class(
                path="math",
                is_member_callable=1,
            )

    def test_should_pre_allocate_module_when_enabled(
        self,
        target_class,
    ):
        target = target_class(
            path="math",
            is_pre_allocated=True,
        )

        assert target.allocated_module is importlib.import_module(
            "math"
        )

    def test_should_return_name_when_name_property_is_read(
        self,
        target,
    ):
        assert target.name == "math"

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="empty-string"),
            pytest.param(100, id="integer"),
            pytest.param((), id="tuple"),
        ],
    )
    def test_should_raise_value_error_when_name_property_is_invalid(
        self,
        target,
        value,
    ):
        with pytest.raises(
            ValueError,
            match="'name'",
        ):
            target.name = value

    def test_should_update_name_when_name_property_is_valid(
        self,
        target,
    ):
        target.name = "math_module"

        assert target.name == "math_module"

    def test_should_return_path_when_path_property_is_read(
        self,
        target,
    ):
        assert target.path == "math"

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="empty-string"),
            pytest.param(100, id="integer"),
            pytest.param((), id="tuple"),
        ],
    )
    def test_should_raise_value_error_when_path_property_is_invalid(
        self,
        target,
        value,
    ):
        with pytest.raises(
            ValueError,
            match="'path'",
        ):
            target.path = value

    def test_should_update_path_when_path_property_is_valid(
        self,
        target,
    ):
        target.path = "json"

        assert target.path == "json"

    def test_should_return_package_when_package_property_is_read(
        self,
        target,
    ):
        assert target.package is None

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(100, id="integer"),
            pytest.param((), id="tuple"),
            pytest.param([], id="list"),
        ],
    )
    def test_should_raise_type_error_when_package_property_is_invalid(
        self,
        target,
        value,
    ):
        with pytest.raises(
            TypeError,
            match="'package'",
        ):
            target.package = value

    def test_should_normalize_empty_package_property_to_none(
        self,
        target,
    ):
        target.package = ""

        assert target.package is None

    def test_should_update_package_when_package_property_is_valid(
        self,
        target,
    ):
        target.package = "xml"

        assert target.package == "xml"

    def test_should_return_member_when_member_property_is_read(
        self,
        target,
    ):
        assert target.member == ""

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(100, id="integer"),
            pytest.param((), id="tuple"),
            pytest.param([], id="list"),
        ],
    )
    def test_should_raise_type_error_when_member_property_is_invalid(
        self,
        target,
        value,
    ):
        with pytest.raises(
            TypeError,
            match="'member'",
        ):
            target.member = value

    def test_should_normalize_empty_member_property_to_none(
        self,
        target,
    ):
        target.member = ""

        assert target.member is None

    def test_should_update_member_when_member_property_is_valid(
        self,
        target,
    ):
        target.member = "sqrt"

        assert target.member == "sqrt"

    def test_should_return_callable_flag_when_property_is_read(
        self,
        target,
    ):
        assert target.is_member_callable is False

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(None, id="none"),
            pytest.param(1, id="integer"),
            pytest.param("true", id="string"),
            pytest.param([], id="list"),
        ],
    )
    def test_should_raise_value_error_when_callable_flag_is_invalid(
        self,
        target,
        value,
    ):
        with pytest.raises(
            ValueError,
            match="'is_member_callable'",
        ):
            target.is_member_callable = value

    def test_should_update_callable_flag_when_property_is_valid(
        self,
        target,
    ):
        target.is_member_callable = True

        assert target.is_member_callable is True

    def test_should_return_pre_allocation_flag_when_property_is_read(
        self,
        target,
    ):
        assert target.is_pre_allocated is False

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(None, id="none"),
            pytest.param(1, id="integer"),
            pytest.param("true", id="string"),
            pytest.param([], id="list"),
        ],
    )
    def test_should_raise_type_error_when_pre_allocation_flag_is_invalid(
        self,
        target,
        value,
    ):
        with pytest.raises(
            TypeError,
            match="'is_pre_allocated'",
        ):
            target.is_pre_allocated = value

    def test_should_update_pre_allocation_flag_when_property_is_valid(
        self,
        target,
    ):
        target.is_pre_allocated = True

        assert target.is_pre_allocated is True

    def test_should_return_allocated_module_when_property_is_read(
        self,
        target,
    ):
        assert target.allocated_module is None

    def test_should_update_allocated_module_when_property_is_set(
        self,
        target,
    ):
        target.allocated_module = "allocated"

        assert target.allocated_module == "allocated"

    def test_should_allocate_module_when_allocate_is_called(
        self,
        target,
    ):
        result = target.allocate()

        assert result is importlib.import_module("math")

    def test_should_return_cached_module_when_allocate_is_called_repeatedly(
        self,
        target,
    ):
        first_result = target.allocate()
        second_result = target.allocate()

        assert first_result is second_result

    def test_should_import_module_without_package_when_package_is_none(
        self,
        target,
    ):
        result = target.allocate()

        assert result is importlib.import_module("math")

    def test_should_import_module_with_package_when_package_is_defined(
        self,
        target_class,
    ):
        target = target_class(
            path=".etree",
            package="xml",
        )

        result = target.allocate()

        assert result is importlib.import_module(
            ".etree",
            package="xml",
        )

    def test_should_resolve_member_when_member_is_defined(
        self,
        target_class,
    ):
        target = target_class(
            path="math",
            member="sqrt",
        )

        result = target.allocate()

        assert result is importlib.import_module("math").sqrt

    def test_should_resolve_nested_member_when_path_is_nested(
        self,
        target_class,
    ):
        target = target_class(
            path="pathlib",
            member="Path.cwd",
        )

        result = target.allocate()

        assert result == importlib.import_module(
            "pathlib"
        ).Path.cwd

    def test_should_skip_empty_member_segments_when_resolving_member(
        self,
        target_class,
    ):
        target = target_class(
            path="math",
            member="sqrt..",
        )

        assert target.allocate() is importlib.import_module(
            "math"
        ).sqrt

    def test_should_invoke_member_when_callable_flag_is_enabled(
        self,
        target_class,
    ):
        target = target_class(
            path="builtins",
            member="dict",
            is_member_callable=True,
        )

        result = target.allocate()

        assert result == {}

    def test_should_return_member_without_invoking_it_when_callable_flag_is_disabled(
        self,
        target_class,
    ):
        target = target_class(
            path="builtins",
            member="dict",
            is_member_callable=False,
        )

        result = target.allocate()

        assert result is dict

    def test_should_raise_module_not_found_error_when_module_does_not_exist(
        self,
        target_class,
    ):
        target = target_class(
            path="module_that_does_not_exist",
        )

        with pytest.raises(ModuleNotFoundError):
            target.allocate()

    def test_should_raise_attribute_error_when_member_does_not_exist(
        self,
        target_class,
    ):
        target = target_class(
            path="math",
            member="missing_member",
        )

        with pytest.raises(AttributeError):
            target.allocate()

    def test_should_raise_type_error_when_callable_member_cannot_be_invoked(
        self,
        target_class,
    ):
        target = target_class(
            path="math",
            member="sqrt",
            is_member_callable=True,
        )

        with pytest.raises(TypeError):
            target.allocate()

    def test_should_return_none_when_pre_allocation_is_disabled(
        self,
        target,
    ):
        result = target.pre_allocate()

        assert result is None

    def test_should_allocate_module_when_pre_allocation_is_enabled(
        self,
        target_class,
    ):
        target = target_class(
            path="math",
            is_pre_allocated=True,
        )

        result = target.pre_allocate()

        assert result is importlib.import_module("math")

    def test_should_return_none_when_deallocating_unallocated_target(
        self,
        target,
    ):
        result = target.deallocate()

        assert result is None
        assert target.allocated_module is None

    def test_should_clear_allocated_module_when_deallocated(
        self,
        target,
    ):
        target.allocate()

        result = target.deallocate()

        assert result is None
        assert target.allocated_module is None

    def test_should_allocate_module_again_when_reallocated(
        self,
        target,
    ):
        first_result = target.allocate()

        result = target.reallocate()

        assert result is first_result
        assert target.allocated_module is first_result

    def test_should_allocate_module_when_reallocated_before_allocation(
        self,
        target,
    ):
        result = target.reallocate()

        assert result is importlib.import_module("math")

    def test_should_return_true_when_shutdown_is_called(
        self,
        target,
    ):
        result = target.shutdown()

        assert result is True

    def test_should_deallocate_module_when_shutdown_is_called(
        self,
        target,
    ):
        target.allocate()

        result = target.shutdown()

        assert result is True
        assert target.allocated_module is None

    def test_should_return_self_when_context_manager_is_entered(
        self,
        target,
    ):
        with target as result:
            assert result is target

    def test_should_allocate_module_when_context_manager_is_entered(
        self,
        target,
    ):
        with target:
            assert target.allocated_module is not None

    def test_should_deallocate_module_when_context_manager_exits(
        self,
        target,
    ):
        with target:
            pass

        assert target.allocated_module is None

    def test_should_deallocate_module_when_context_manager_exits_with_exception(
        self,
        target,
    ):
        with pytest.raises(RuntimeError):
            with target:
                raise RuntimeError("execution failed")

        assert target.allocated_module is None

    def test_should_preserve_exception_when_context_manager_exits(
        self,
        target,
    ):
        with pytest.raises(
            RuntimeError,
            match="execution failed",
        ):
            with target:
                raise RuntimeError("execution failed")


class ExternalDependencyManagerTest:

    def test_should_return_class_when_factory_is_called(
        self,
        module,
    ):
        result = module.ExternalDependencyManager()

        assert isinstance(result, type)

    def test_should_allocate_classes_when_factory_is_called(
        self,
        module,
    ):
        module.ExternalDependencyManager()

        assert isinstance(module._ImportTarget, type)
        assert isinstance(
            module._ExternalDependencyManager,
            type,
        )

    def test_should_preserve_class_when_factory_is_called_repeatedly(
        self,
        module,
    ):
        first_result = module.ExternalDependencyManager()
        second_result = module.ExternalDependencyManager()

        assert first_result is second_result

    def test_should_initialize_empty_import_targets_when_construct_is_called(
        self,
        manager,
    ):
        assert manager.import_targets == {}

    def test_should_initialize_pre_allocation_as_false(
        self,
        manager,
    ):
        assert manager.is_pre_allocated is False

    def test_should_return_true_when_construct_is_called(
        self,
        manager,
    ):
        result = manager.construct()

        assert result is True

    def test_should_initialize_importlib_dependency_when_construct_is_called(
        self,
        module,
        manager,
    ):
        manager.construct()

        assert module._importlib is importlib

    def test_should_return_existing_singleton_when_requested(
        self,
        manager_class,
    ):
        manager_class._singleton = None

        first_result = manager_class.get_singleton()
        second_result = manager_class.get_singleton()

        assert first_result is second_result

    def test_should_initialize_singleton_when_requested(
        self,
        manager_class,
    ):
        manager_class._singleton = None

        result = manager_class.get_singleton()

        assert isinstance(result, manager_class)

    def test_should_return_self_when_context_manager_is_entered(
        self,
        manager,
    ):
        with manager as result:
            assert result is manager

    def test_should_return_none_when_context_manager_exits(
        self,
        manager,
    ):
        result = manager.__exit__(None, None, None)

        assert result is None

    def test_should_clear_modules_when_context_manager_exits(
        self,
        manager,
    ):
        manager.import_module(path="math")

        with manager:
            assert manager.import_targets

        assert manager.import_targets == {}

    def test_should_clear_modules_when_context_manager_exits_with_exception(
        self,
        manager,
    ):
        manager.import_module(path="math")

        with pytest.raises(
            RuntimeError,
            match="execution failed",
        ):
            with manager:
                raise RuntimeError("execution failed")

        assert manager.import_targets == {}

    def test_should_return_pre_allocation_flag_when_property_is_read(
        self,
        manager,
    ):
        assert manager.is_pre_allocated is False

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(None, id="none"),
            pytest.param(1, id="integer"),
            pytest.param("true", id="string"),
            pytest.param([], id="list"),
        ],
    )
    def test_should_raise_type_error_when_pre_allocation_property_is_invalid(
        self,
        manager,
        value,
    ):
        with pytest.raises(
            TypeError,
            match="'value'",
        ):
            manager.is_pre_allocated = value

    def test_should_update_pre_allocation_property_when_value_is_valid(
        self,
        manager,
    ):
        manager.is_pre_allocated = True

        assert manager.is_pre_allocated is True

    def test_should_return_import_targets_when_property_is_read(
        self,
        manager,
    ):
        assert manager.import_targets == {}

    def test_should_raise_value_error_when_import_targets_is_empty(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="non-empty dictionary",
        ):
            manager.import_targets = {}

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(None, id="none"),
            pytest.param([], id="list"),
            pytest.param((), id="tuple"),
            pytest.param("invalid", id="string"),
        ],
    )
    def test_should_raise_value_error_when_import_targets_is_not_dictionary(
        self,
        manager,
        value,
    ):
        with pytest.raises(
            ValueError,
            match="non-empty dictionary",
        ):
            manager.import_targets = value

    def test_should_raise_value_error_when_import_target_key_is_empty(
        self,
        manager,
        target,
    ):
        with pytest.raises(
            ValueError,
            match="keys must be non-empty strings",
        ):
            manager.import_targets = {"": target}

    def test_should_raise_value_error_when_import_target_key_is_invalid(
        self,
        manager,
        target,
    ):
        with pytest.raises(
            ValueError,
            match="keys must be non-empty strings",
        ):
            manager.import_targets = {100: target}

    def test_should_raise_value_error_when_import_target_value_is_invalid(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="values must be ImportTarget instances",
        ):
            manager.import_targets = {"math": object()}

    def test_should_update_import_targets_when_dictionary_is_valid(
        self,
        manager,
        target,
    ):
        manager.import_targets = {"math": target}

        assert manager.import_targets == {"math": target}

    def test_should_return_true_when_setup_receives_valid_empty_targets(
        self,
        manager,
    ):
        result = manager.setup(import_targets=())

        assert result is True

    def test_should_return_true_when_setup_receives_empty_target_list(
        self,
        manager,
    ):
        result = manager.setup(import_targets=[])

        assert result is True

    def test_should_raise_value_error_when_setup_receives_empty_arguments(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.*non-empty dictionary",
        ):
            manager.setup()

    def test_should_raise_value_error_when_setup_targets_are_invalid_type(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.import_targets",
        ):
            manager.setup(import_targets="math")

    def test_should_raise_value_error_when_setup_pre_allocation_is_invalid(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.is_pre_allocated",
        ):
            manager.setup(
                import_targets=(),
                is_pre_allocated=1,
            )

    @pytest.mark.parametrize(
        "target_kwargs",
        [
            pytest.param(None, id="none"),
            pytest.param({}, id="empty-dictionary"),
            pytest.param("math", id="string"),
            pytest.param(100, id="integer"),
            pytest.param([], id="list"),
        ],
    )
    def test_should_raise_value_error_when_setup_target_is_invalid(
        self,
        manager,
        target_kwargs,
    ):
        with pytest.raises(
            ValueError,
            match="import_targets\\[\\]",
        ):
            manager.setup(
                import_targets=(target_kwargs,),
            )

    def test_should_register_target_when_setup_receives_valid_target(
        self,
        manager,
    ):
        result = manager.setup(
            import_targets=(
                {"path": "math"},
            ),
        )

        assert result is True
        assert "math" in manager.import_targets

    def test_should_register_multiple_targets_when_setup_receives_multiple(
        self,
        manager,
    ):
        manager.setup(
            import_targets=(
                {"path": "math"},
                {"path": "json"},
                {"path": "pathlib"},
            ),
        )

        assert set(manager.import_targets) == {
            "math",
            "json",
            "pathlib",
        }

    def test_should_apply_manager_pre_allocation_to_registered_targets(
        self,
        manager,
    ):
        manager.setup(
            import_targets=(
                {"path": "math"},
            ),
            is_pre_allocated=True,
        )

        assert manager.import_targets["math"].is_pre_allocated is True
        assert manager.import_targets["math"].allocated_module is (
            importlib.import_module("math")
        )

    def test_should_preserve_existing_pre_allocation_when_setup_omits_flag(
        self,
        manager,
    ):
        manager.is_pre_allocated = True

        manager.setup(
            import_targets=(
                {"path": "math"},
            ),
        )

        assert manager.is_pre_allocated is True
        assert manager.import_targets["math"].is_pre_allocated is True

    def test_should_update_pre_allocation_when_setup_receives_flag(
        self,
        manager,
    ):
        manager.setup(
            import_targets=(),
            is_pre_allocated=True,
        )

        assert manager.is_pre_allocated is True

    def test_should_ignore_duplicate_target_when_setup_registers_existing_name(
        self,
        manager,
    ):
        manager.setup(
            import_targets=(
                {"path": "math"},
            ),
        )

        original_target = manager.import_targets["math"]

        manager.setup(
            import_targets=(
                {"path": "json", "name": "math"},
            ),
        )

        assert manager.import_targets["math"] is original_target
        assert len(manager.import_targets) == 1

    def test_should_register_target_using_custom_name_when_setup_is_called(
        self,
        manager,
    ):
        manager.setup(
            import_targets=(
                {
                    "path": "math",
                    "name": "math_module",
                },
            ),
        )

        assert "math_module" in manager.import_targets

    def test_should_rollback_staged_targets_when_setup_fails(
        self,
        manager,
    ):
        with pytest.raises(ModuleNotFoundError):
            manager.setup(
                import_targets=(
                    {"path": "math", "is_pre_allocated": True},
                    {
                        "path": "module_that_does_not_exist",
                        "is_pre_allocated": True,
                    },
                ),
                is_pre_allocated=True,
            )

        assert manager.import_targets == {}

    def test_should_preserve_existing_targets_when_setup_fails(
        self,
        manager,
    ):
        manager.setup(
            import_targets=(
                {"path": "math"},
            ),
        )

        original_target = manager.import_targets["math"]

        with pytest.raises(ModuleNotFoundError):
            manager.setup(
                import_targets=(
                    {"path": "json"},
                    {"path": "module_that_does_not_exist"},
                ),
            )

        assert manager.import_targets == {"math": original_target}

    def test_should_deallocate_staged_targets_when_setup_fails(
        self,
        manager,
        monkeypatch,
    ):
        deallocated_targets = []
        original_target_class = (
            external_dependency_manager._ImportTarget
        )

        class TrackingImportTarget(original_target_class):

            def deallocate(self):
                deallocated_targets.append(self.name)
                return super().deallocate()

        monkeypatch.setattr(
            external_dependency_manager,
            "_ImportTarget",
            TrackingImportTarget,
        )

        with pytest.raises(ModuleNotFoundError):
            manager.setup(
                import_targets=(
                    {"path": "math"},
                    {"path": "module_that_does_not_exist"},
                ),
                is_pre_allocated=True,
            )

        assert deallocated_targets == ["math"]

    def test_should_return_true_when_import_modules_receives_empty_tuple(
        self,
        manager,
    ):
        result = manager.import_modules(())

        assert result is True

    def test_should_return_true_when_import_modules_receives_empty_list(
        self,
        manager,
    ):
        result = manager.import_modules([])

        assert result is True

    @pytest.mark.parametrize(
        "targets",
        [
            pytest.param(None, id="none"),
            pytest.param("math", id="string"),
            pytest.param({}, id="dictionary"),
            pytest.param(100, id="integer"),
        ],
    )
    def test_should_raise_value_error_when_import_modules_receives_invalid_type(
        self,
        manager,
        targets,
    ):
        with pytest.raises(
            ValueError,
            match="'targets'",
        ):
            manager.import_modules(targets)

    @pytest.mark.parametrize(
        "target",
        [
            pytest.param(None, id="none"),
            pytest.param({}, id="empty-dictionary"),
            pytest.param("math", id="string"),
            pytest.param(100, id="integer"),
            pytest.param([], id="list"),
        ],
    )
    def test_should_raise_value_error_when_import_modules_target_is_invalid(
        self,
        manager,
        target,
    ):
        with pytest.raises(
            ValueError,
            match="targets\\[\\]",
        ):
            manager.import_modules((target,))

    def test_should_import_multiple_modules_when_targets_are_valid(
        self,
        manager,
    ):
        result = manager.import_modules(
            (
                {"path": "math"},
                {"path": "json"},
            ),
        )

        assert result is True
        assert set(manager.import_targets) == {"math", "json"}

    def test_should_import_module_when_import_module_is_called(
        self,
        manager,
    ):
        allocate = manager.import_module(path="math")

        assert callable(allocate)
        assert allocate() is importlib.import_module("math")

    def test_should_raise_value_error_when_import_module_receives_empty_arguments(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.*non-empty dictionary",
        ):
            manager.import_module()

    def test_should_raise_value_error_when_import_module_name_is_invalid(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.name",
        ):
            manager.import_module(
                name=100,
                path="math",
            )

    def test_should_raise_value_error_when_import_module_path_is_missing(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="kwargs.path",
        ):
            manager.import_module(name="math_module")

    def test_should_use_path_as_registry_key_when_name_is_omitted(
        self,
        manager,
    ):
        manager.import_module(path="math")

        assert "math" in manager.import_targets

    def test_should_use_name_as_registry_key_when_name_is_provided(
        self,
        manager,
    ):
        manager.import_module(
            path="math",
            name="math_module",
        )

        assert "math_module" in manager.import_targets

    def test_should_return_existing_allocate_method_when_target_is_registered(
        self,
        manager,
    ):
        first_result = manager.import_module(path="math")
        second_result = manager.import_module(path="math")

        assert first_result.__self__ is second_result.__self__

    def test_should_preserve_existing_target_when_duplicate_name_is_imported(
        self,
        manager,
    ):
        first_result = manager.import_module(
            path="math",
            name="shared",
        )

        second_result = manager.import_module(
            path="json",
            name="shared",
        )

        assert first_result.__self__ is second_result.__self__
        assert manager.import_targets["shared"].path == "math"

    def test_should_apply_manager_pre_allocation_when_importing_module(
        self,
        manager,
    ):
        manager.is_pre_allocated = True

        allocate = manager.import_module(path="math")

        assert allocate.__self__.allocated_module is (
            importlib.import_module("math")
        )

    def test_should_return_true_when_unload_modules_receives_empty_tuple(
        self,
        manager,
    ):
        result = manager.unload_modules(())

        assert result is True

    def test_should_return_true_when_unload_modules_receives_empty_list(
        self,
        manager,
    ):
        result = manager.unload_modules([])

        assert result is True

    @pytest.mark.parametrize(
        "names",
        [
            pytest.param(None, id="none"),
            pytest.param("math", id="string"),
            pytest.param({}, id="dictionary"),
            pytest.param(100, id="integer"),
        ],
    )
    def test_should_raise_value_error_when_unload_modules_receives_invalid_type(
        self,
        manager,
        names,
    ):
        with pytest.raises(
            ValueError,
            match="'names'",
        ):
            manager.unload_modules(names)

    @pytest.mark.parametrize(
        "name",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="empty-string"),
            pytest.param(100, id="integer"),
            pytest.param((), id="tuple"),
        ],
    )
    def test_should_raise_value_error_when_unload_modules_name_is_invalid(
        self,
        manager,
        name,
    ):
        with pytest.raises(
            ValueError,
            match="'name'",
        ):
            manager.unload_modules((name,))

    def test_should_unload_module_when_name_is_registered(
        self,
        manager,
    ):
        manager.import_module(path="math")

        result = manager.unload_module("math")

        assert result is True
        assert "math" not in manager.import_targets

    def test_should_raise_value_error_when_unload_module_name_is_invalid(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="'name'",
        ):
            manager.unload_module("")

    def test_should_raise_value_error_when_unload_module_name_is_not_string(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="'name'",
        ):
            manager.unload_module(100)

    def test_should_raise_value_error_when_unload_module_name_is_unknown(
        self,
        manager,
    ):
        with pytest.raises(
            ValueError,
            match="collection item",
        ):
            manager.unload_module("unknown")

    def test_should_unload_multiple_modules_when_names_are_registered(
        self,
        manager,
    ):
        manager.import_modules(
            (
                {"path": "math"},
                {"path": "json"},
                {"path": "pathlib"},
            ),
        )

        result = manager.unload_modules(
            ("math", "json", "pathlib"),
        )

        assert result is True
        assert manager.import_targets == {}

    def test_should_clear_modules_when_registry_contains_targets(
        self,
        manager,
    ):
        manager.import_modules(
            (
                {"path": "math"},
                {"path": "json"},
            ),
        )

        result = manager.clear_modules()

        assert result is True
        assert manager.import_targets == {}

    def test_should_return_true_when_clear_modules_receives_empty_registry(
        self,
        manager,
    ):
        result = manager.clear_modules()

        assert result is True
        assert manager.import_targets == {}

    def test_should_return_true_when_shutdown_is_called(
        self,
        manager,
    ):
        result = manager.shutdown()

        assert result is True

    def test_should_clear_registered_modules_when_shutdown_is_called(
        self,
        manager,
    ):
        manager.import_modules(
            (
                {"path": "math"},
                {"path": "json"},
            ),
        )

        result = manager.shutdown()

        assert result is True
        assert manager.import_targets == {}

    def test_should_complete_repeated_module_imports_without_registry_growth(
        self,
        manager,
    ):
        for _ in range(100):
            manager.import_module(path="math")

        assert len(manager.import_targets) == 1

    def test_should_complete_repeated_module_allocation_without_reimporting(
        self,
        manager,
        monkeypatch,
    ):
        import_calls = []
        original_import_module = importlib.import_module

        def tracked_import_module(*args, **kwargs):
            import_calls.append(args[0])

            return original_import_module(*args, **kwargs)

        monkeypatch.setattr(
            external_dependency_manager._importlib,
            "import_module",
            tracked_import_module,
        )

        allocate = manager.import_module(path="math")

        for _ in range(100):
            allocate()

        assert import_calls == ["math"]

    def test_should_preserve_registered_targets_after_repeated_setup(
        self,
        manager,
    ):
        for _ in range(100):
            manager.setup(
                import_targets=(
                    {"path": "math"},
                    {"path": "json"},
                ),
            )

        assert set(manager.import_targets) == {"math", "json"}

    def test_should_complete_repeated_import_and_unload_operations(
        self,
        manager,
    ):
        for _ in range(100):
            manager.import_module(path="math")
            manager.unload_module("math")

        assert manager.import_targets == {}

    def test_should_clear_all_targets_after_repeated_shutdown(
        self,
        manager,
    ):
        for _ in range(10):
            manager.import_modules(
                (
                    {"path": "math"},
                    {"path": "json"},
                ),
            )

            assert manager.shutdown() is True
            assert manager.import_targets == {}

    def test_should_preserve_module_identity_after_repeated_allocation(
        self,
        manager,
    ):
        allocate = manager.import_module(path="json")

        results = tuple(
            allocate()
            for _ in range(100)
        )

        assert all(
            result is results[0]
            for result in results
        )

    def test_should_reallocate_module_after_unloading_and_importing_again(
        self,
        manager,
    ):
        first_allocate = manager.import_module(path="math")
        first_module = first_allocate()

        manager.unload_module("math")

        second_allocate = manager.import_module(path="math")
        second_module = second_allocate()

        assert first_module is second_module
        assert first_allocate.__self__ is not second_allocate.__self__

    def test_should_preserve_independent_manager_registries(
        self,
        manager_class,
    ):
        first_manager = manager_class()
        second_manager = manager_class()

        first_manager.import_module(path="math")

        assert "math" in first_manager.import_targets
        assert second_manager.import_targets == {}

    def test_should_propagate_module_import_exception(
        self,
        manager,
    ):
        with pytest.raises(ModuleNotFoundError):
            manager.import_module(
                path="module_that_does_not_exist",
            )()

    def test_should_preserve_registry_after_module_import_exception(
        self,
        manager,
    ):
        allocate = manager.import_module(
            path="module_that_does_not_exist",
        )

        with pytest.raises(ModuleNotFoundError):
            allocate()

        assert "module_that_does_not_exist" in manager.import_targets

    def test_should_preserve_existing_registry_after_failed_import(
        self,
        manager,
    ):
        manager.import_module(path="math")

        with pytest.raises(ModuleNotFoundError):
            manager.import_module(
                path="module_that_does_not_exist",
            )()

        assert "math" in manager.import_targets
        assert "module_that_does_not_exist" in manager.import_targets

@pytest.fixture
def manager_module():
    return importlib.reload(
        importlib.import_module(
            "qlogicae_cor.v3.library.enum_conversion_value_enum_manager"
        )
    )


@pytest.fixture
def enum_class():
    class EnumConversionValue(StrEnum):
        STRING = "string"
        ENUM = "enum"
        CUSTOM = "custom"
        NONE = "none"

    return EnumConversionValue


@pytest.fixture
def dependency_manager_module():
    return importlib.import_module(
        "qlogicae_cor.v3.library.external_dependency_manager"
    )


@pytest.fixture
def dependency_calls(
    monkeypatch,
    dependency_manager_module,
    enum_class,
):
    calls = []

    class FakeExternalDependencyManager:
        @classmethod
        def get_singleton(cls):
            return cls()

        def import_module(self, **kwargs):
            calls.append(kwargs)
            return lambda: enum_class

    def external_dependency_manager_factory():
        return FakeExternalDependencyManager

    monkeypatch.setattr(
        dependency_manager_module,
        "ExternalDependencyManager",
        external_dependency_manager_factory,
    )

    return calls


@pytest.fixture
def manager_class(manager_module, dependency_calls):
    return manager_module.EnumConversionValueEnumManager()


@pytest.fixture
def manager(manager_class):
    return manager_class()


class TestEnumConversionValueEnumManagerAllocation:
    def test_should_export_manager_factory(self, manager_module):
        assert manager_module.__all__ == (
            "EnumConversionValueEnumManager",
        )

    def test_should_initialize_manager_class_lazily(self, manager_module):
        assert manager_module._EnumConversionValueEnumManager is None

        manager_class = manager_module.EnumConversionValueEnumManager()

        assert isinstance(manager_class, type)
        assert (
            manager_module._EnumConversionValueEnumManager
            is manager_class
        )

    def test_should_replace_allocator_after_allocation(
        self,
        manager_module,
    ):
        manager_module.EnumConversionValueEnumManager()

        assert manager_module._allocate() is None

    def test_should_return_same_manager_class(self, manager_module):
        first_class = manager_module.EnumConversionValueEnumManager()
        second_class = manager_module.EnumConversionValueEnumManager()

        assert first_class is second_class

    def test_should_initialize_singleton_as_none(self, manager_class):
        assert manager_class._singleton is None


class TestEnumConversionValueEnumManagerConstruction:
    def test_should_construct_manager(self, manager):
        assert manager is not None

    def test_should_initialize_external_dependency_manager(
        self,
        manager_module,
        manager,
    ):
        assert callable(manager_module._ExternalDependencyManager)

    def test_should_initialize_enum_conversion_value(
        self,
        manager_module,
        manager,
        enum_class,
    ):
        assert manager_module._EnumConversionValue() is enum_class

    def test_should_import_enum_conversion_value(
        self,
        dependency_calls,
        manager,
    ):
        assert dependency_calls == [
            {
                "path": ".enum_conversion_value",
                "package": "qlogicae_cor.v3.library",
                "member": "EnumConversionValue",
                "is_member_callable": True,
            }
        ]

    def test_should_return_true_when_constructing(self, manager):
        assert manager.construct() is True

    def test_should_initialize_dependencies_when_reconstructing(
        self,
        manager_module,
        manager,
        dependency_calls,
    ):
        previous_calls = len(dependency_calls)

        assert manager.construct() is True
        assert len(dependency_calls) == previous_calls + 1

    def test_should_replace_enum_conversion_value_dependency(
        self,
        manager_module,
        manager,
        enum_class,
    ):
        manager.construct()

        assert manager_module._EnumConversionValue() is enum_class


class TestEnumConversionValueEnumManagerLifecycle:
    def test_should_return_true_when_setup_receives_no_arguments(
        self,
        manager,
    ):
        with pytest.raises(ValueError):
            manager.setup()

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"value": "string"},
            {"value": None},
            {"value": ""},
            {"value": 0},
            {"value": False},
            {"value": []},
            {"value": {}},
            {"first": "string", "second": "enum"},
        ],
    )
    def test_should_return_true_when_setup_receives_arguments(
        self,
        manager,
        kwargs,
    ):
        assert manager.setup(**kwargs) is True

    def test_should_return_true_when_shutdown_is_called(self, manager):
        assert manager.shutdown() is True

    def test_should_return_manager_when_entering_context(self, manager):
        with manager as entered_manager:
            assert entered_manager is manager

    def test_should_shutdown_when_exiting_context(
        self,
        manager,
        monkeypatch,
    ):
        calls = []

        def shutdown():
            calls.append(True)
            return True

        monkeypatch.setattr(manager, "shutdown", shutdown)

        with manager:
            pass

        assert calls == [True]

    def test_should_propagate_exception_when_exiting_context(self, manager):
        with pytest.raises(RuntimeError, match="context failure"):
            with manager:
                raise RuntimeError("context failure")


class TestEnumConversionValueEnumManagerSingleton:
    def test_should_create_singleton_when_none_exists(self, manager_class):
        singleton = manager_class.get_singleton()

        assert isinstance(singleton, manager_class)
        assert manager_class._singleton is singleton

    def test_should_return_existing_singleton(self, manager_class):
        first_singleton = manager_class.get_singleton()
        second_singleton = manager_class.get_singleton()

        assert first_singleton is second_singleton

    def test_should_create_new_singleton_after_reset(self, manager_class):
        first_singleton = manager_class.get_singleton()

        manager_class._singleton = None

        second_singleton = manager_class.get_singleton()

        assert second_singleton is not first_singleton
        assert manager_class._singleton is second_singleton

    def test_should_construct_singleton_dependencies(
        self,
        manager_class,
        dependency_calls,
    ):
        singleton = manager_class.get_singleton()

        assert singleton is manager_class._singleton
        assert dependency_calls


class TestEnumConversionValueEnumManagerConvertValue:
    @pytest.mark.parametrize(
        ("input_type", "expected"),
        [
            ("string", "string"),
            ("enum", "enum"),
            ("custom", "custom"),
            ("none", "none"),
            ("unknown", "none"),
            ("invalid", "none"),
            ("", "none"),
            (None, "none"),
            (100, "none"),
            ([], "none"),
            ({}, "none"),
        ],
    )
    def test_should_convert_input_to_string_by_default(
        self,
        manager,
        input_type,
        expected,
    ):
        assert manager.convert_value(input_type) == expected

    @pytest.mark.parametrize(
        ("input_type", "expected"),
        [
            ("string", "string"),
            ("enum", "enum"),
            ("custom", "custom"),
            ("none", "none"),
            ("unknown", "none"),
            ("invalid", "none"),
            ("", "none"),
            (None, "none"),
            (100, "none"),
        ],
    )
    def test_should_convert_input_to_string_when_output_is_string(
        self,
        manager,
        enum_class,
        input_type,
        expected,
    ):
        assert (
            manager.convert_value(
                input_type,
                enum_class.STRING,
            )
            == expected
        )

    @pytest.mark.parametrize(
        ("input_type", "expected"),
        [
            ("string", "string"),
            ("STRING", "string"),
            ("String", "string"),
            ("enum", "none"),
            ("none", "enum"),
            ("NONE", "enum"),
            ("custom", "custom"),
            ("CUSTOM", "custom"),
            ("unknown", "none"),
            ("invalid", "none"),
            ("", "none"),
            (None, "enum"),
            (100, "none"),
            ([], "none"),
            ({}, "none"),
        ],
    )
    def test_should_convert_input_to_enum(
        self,
        manager,
        enum_class,
        input_type,
        expected,
    ):
        assert (
            manager.convert_value(
                input_type,
                enum_class.ENUM,
            )
            == enum_class(expected)
        )

    @pytest.mark.parametrize(
        "output_type",
        [
            "custom",
            "none",
            "invalid",
            100,
            [],
            {},
        ],
    )
    def test_should_return_none_for_unsupported_output_type(
        self,
        manager,
        enum_class,
        output_type,
    ):
        assert (
            manager.convert_value(
                enum_class.STRING,
                output_type,
            )
            == enum_class.NONE
        )

    def test_should_use_string_output_when_output_type_is_none(
        self,
        manager,
        enum_class,
    ):
        assert (
            manager.convert_value(
                enum_class.STRING,
                None,
            )
            == "string"
        )

    def test_should_return_enum_for_none_input_and_enum_output(
        self,
        manager,
        enum_class,
    ):
        assert (
            manager.convert_value(
                None,
                enum_class.ENUM,
            )
            == enum_class.ENUM
        )

    def test_should_return_custom_for_custom_input_and_enum_output(
        self,
        manager,
        enum_class,
    ):
        assert (
            manager.convert_value(
                "custom",
                enum_class.ENUM,
            )
            == enum_class.CUSTOM
        )

    def test_should_return_none_for_unknown_input_and_enum_output(
        self,
        manager,
        enum_class,
    ):
        assert (
            manager.convert_value(
                "unsupported",
                enum_class.ENUM,
            )
            == enum_class.NONE
        )

    def test_should_return_none_for_unsupported_output_and_input(
        self,
        manager,
        enum_class,
    ):
        assert (
            manager.convert_value(
                "unsupported",
                "unsupported",
            )
            == enum_class.NONE
        )


class TestEnumConversionValueEnumManagerStress:
    def test_should_reuse_manager_class_across_repeated_allocations(
        self,
        manager_module,
    ):
        manager_classes = [
            manager_module.EnumConversionValueEnumManager()
            for _ in range(100)
        ]

        assert all(
            manager_class is manager_classes[0]
            for manager_class in manager_classes
        )

    def test_should_reuse_singleton_across_repeated_calls(
        self,
        manager_class,
    ):
        singletons = [
            manager_class.get_singleton()
            for _ in range(100)
        ]

        assert all(
            singleton is singletons[0]
            for singleton in singletons
        )

    def test_should_convert_values_repeatedly(
        self,
        manager,
        enum_class,
    ):
        results = [
            manager.convert_value(
                enum_class.STRING,
                enum_class.STRING,
            )
            for _ in range(100)
        ]

        assert results == ["string"] * 100


class TestEnumConversionValueEnumManagerMissingConversionCases:

    def test_should_use_string_output_when_output_type_is_explicitly_none(
        self,
        manager,
        enum_class,
    ):
        result = manager.convert_value(
            enum_class.STRING,
            None,
        )

        assert result == "string"

    @pytest.mark.parametrize(
        ("input_type", "expected_value"),
        [
            ("String", "string"),
            ("StRiNg", "string"),
            ("Enum", "none"),
            ("EnUm", "none"),
            ("Custom", "custom"),
            ("CuStOm", "custom"),
            ("None", "enum"),
            ("NoNe", "enum"),
        ],
    )
    def test_should_convert_mixed_case_input_to_enum(
        self,
        manager,
        enum_class,
        input_type,
        expected_value,
    ):
        result = manager.convert_value(
            input_type,
            enum_class.ENUM,
        )

        assert result == enum_class(expected_value)

    @pytest.mark.parametrize(
        ("input_type", "expected"),
        [
            ("STRING", "STRING"),
            ("ENUM", "NONE"),
            ("CUSTOM", "CUSTOM"),
            ("NONE", "ENUM"),
        ],
    )
    def test_should_convert_enum_member_to_enum(
        self,
        manager,
        enum_class,
        input_type,
        expected,
    ):
        result = manager.convert_value(
            getattr(enum_class, input_type),
            enum_class.ENUM,
        )

        assert result is getattr(enum_class, expected)
        
    def test_should_return_none_when_direct_exit_is_called(
        self,
        manager,
    ):
        result = manager.__exit__(None, None, None)

        assert result is None

    def test_should_not_suppress_exception_when_direct_exit_is_called(
        self,
        manager,
    ):
        exception = RuntimeError("execution failed")

        result = manager.__exit__(
            RuntimeError,
            exception,
            exception.__traceback__,
        )

        assert result is None


class TestEnumConversionValueEnumManagerDependencyFailures:

    def test_should_propagate_dependency_import_error(
        self,
        manager_module,
        dependency_manager_module,
        monkeypatch,
    ):
        class FakeExternalDependencyManager:

            def get_singleton(self):
                return self

            def import_module(self, **kwargs):
                raise ImportError("dependency unavailable")

        monkeypatch.setattr(
            dependency_manager_module,
            "ExternalDependencyManager",
            FakeExternalDependencyManager,
        )

        manager_class = manager_module.EnumConversionValueEnumManager()

        with pytest.raises(
            ImportError,
            match="dependency unavailable",
        ):
            manager_class()

        assert manager_class._singleton is None

    def test_should_allow_construction_after_dependency_import_failure(
        self,
        manager_module,
        dependency_manager_module,
        enum_class,
        monkeypatch,
    ):
        should_fail = True

        class FakeExternalDependencyManager:

            def get_singleton(self):
                return self

            def import_module(self, **kwargs):
                if should_fail:
                    raise ImportError("dependency unavailable")

                return lambda: enum_class

        monkeypatch.setattr(
            dependency_manager_module,
            "ExternalDependencyManager",
            FakeExternalDependencyManager,
        )

        manager_class = manager_module.EnumConversionValueEnumManager()

        with pytest.raises(ImportError):
            manager_class()

        should_fail = False

        manager = manager_class()

        assert isinstance(manager, manager_class)
        assert manager_class._singleton is None

    def test_should_propagate_dependency_manager_initialization_error(
        self,
        manager_module,
        dependency_manager_module,
        monkeypatch,
    ):
        class FakeExternalDependencyManager:

            def __init__(self):
                raise RuntimeError("initialization failed")

        monkeypatch.setattr(
            dependency_manager_module,
            "ExternalDependencyManager",
            FakeExternalDependencyManager,
        )

        manager_class = manager_module.EnumConversionValueEnumManager()

        with pytest.raises(
            RuntimeError,
            match="initialization failed",
        ):
            manager_class()

        assert manager_class._singleton is None
