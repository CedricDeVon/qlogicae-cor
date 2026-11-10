
import importlib
from unittest.mock import Mock, patch

import pytest

import qlogicae_cor.v3.library.group_selection_manager as module
from qlogicae_cor.v3.library.group_selection_manager import (
    GroupSelectionManager,
)


pytestmark = pytest.mark.timeout(2)


class TestGroupSelectionManager:
    @pytest.fixture
    def manager(self):
        return GroupSelectionManager()()

    def test_should_export_manager_factory_when_module_is_imported(
        self,
    ) -> None:
        assert module.__all__ == ("GroupSelectionManager",)

    def test_should_return_manager_class_when_factory_is_called(
        self,
    ) -> None:
        assert isinstance(GroupSelectionManager(), type)

    def test_should_return_same_class_when_factory_is_called_repeatedly(
        self,
    ) -> None:
        first_class = GroupSelectionManager()
        second_class = GroupSelectionManager()

        assert first_class is second_class

    def test_should_allocate_manager_class_when_class_is_uninitialized(
        self,
    ) -> None:
        importlib.reload(module)

        assert module._GroupSelectionManager is None

        manager_class = module.GroupSelectionManager()

        assert isinstance(manager_class, type)
        assert module._GroupSelectionManager is manager_class

    def test_should_replace_allocator_when_class_is_allocated(self) -> None:
        importlib.reload(module)

        module.GroupSelectionManager()

        assert module._allocate() is None

    def test_should_not_allocate_class_when_class_is_initialized(
        self,
        monkeypatch,
    ) -> None:
        manager_class = GroupSelectionManager()

        def unexpected_allocation():
            pytest.fail("Unexpected allocation")

        monkeypatch.setattr(
            module,
            "_allocate",
            unexpected_allocation,
        )

        assert module.GroupSelectionManager() is manager_class

    def test_should_initialize_instance_when_constructed(
        self,
        manager,
    ) -> None:
        assert isinstance(manager, type(manager))

    def test_should_return_true_when_construct_is_called(
        self,
        manager,
    ) -> None:
        assert manager.construct() is True

    def test_should_return_true_when_shutdown_is_called(
        self,
        manager,
    ) -> None:
        assert manager.shutdown() is True

    def test_should_return_same_instance_when_singleton_is_requested(
        self,
        manager,
    ) -> None:
        manager_class = type(manager)
        manager_class._singleton = None

        first_instance = manager_class.get_singleton()
        second_instance = manager_class.get_singleton()

        assert first_instance is second_instance

    def test_should_create_instance_when_singleton_is_uninitialized(
        self,
        manager,
    ) -> None:
        manager_class = type(manager)
        manager_class._singleton = None

        instance = manager_class.get_singleton()

        assert isinstance(instance, manager_class)
        assert manager_class._singleton is instance

    def test_should_reinitialize_singleton_when_singleton_is_reset(
        self,
        manager,
    ) -> None:
        manager_class = type(manager)
        manager_class._singleton = None

        first_instance = manager_class.get_singleton()
        manager_class._singleton = None
        second_instance = manager_class.get_singleton()

        assert second_instance is not first_instance

    def test_should_return_same_instance_when_context_is_entered(
        self,
        manager,
    ) -> None:
        with manager as entered_instance:
            assert entered_instance is manager

    def test_should_shutdown_when_context_is_exited(
        self,
        manager,
    ) -> None:
        shutdown = Mock(return_value=True)

        with patch.object(manager, "shutdown", shutdown):
            with manager:
                pass

        shutdown.assert_called_once_with()

    def test_should_shutdown_when_exception_is_raised_in_context(
        self,
        manager,
    ) -> None:
        shutdown = Mock(return_value=True)

        with patch.object(manager, "shutdown", shutdown):
            with pytest.raises(RuntimeError, match="execution failed"):
                with manager:
                    raise RuntimeError("execution failed")

        shutdown.assert_called_once_with()

    def test_should_not_suppress_exception_when_context_is_exited(
        self,
        manager,
    ) -> None:
        with pytest.raises(RuntimeError, match="execution failed"):
            with manager:
                raise RuntimeError("execution failed")

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({"option": "value"}, id="string-option"),
            pytest.param({"option": 123}, id="integer-option"),
            pytest.param({"option": True}, id="boolean-option"),
            pytest.param({"option": None}, id="none-option"),
            pytest.param({"option": []}, id="empty-list-option"),
            pytest.param({"option": {}}, id="empty-dictionary-option"),
            pytest.param({"option": ()}, id="empty-tuple-option"),
            pytest.param({"option": frozenset()}, id="empty-set-option"),
            pytest.param({"option": "特殊字符"}, id="unicode-option"),
            pytest.param(
                {"first": 1, "second": 2},
                id="multiple-options",
            ),
            pytest.param(
                {"option": {"nested": {"value": 1}}},
                id="nested-option",
            ),
        ],
    )
    def test_should_return_true_when_kwargs_are_valid(
        self,
        manager,
        kwargs,
    ) -> None:
        assert manager.setup(**kwargs) is True

    def test_should_raise_value_error_when_kwargs_are_empty(
        self,
        manager,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="'kwargs' must be a non-empty dictionary",
        ):
            manager.setup()

    def test_should_flatten_single_group_when_group_has_children(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {"root": ["first", "second"]},
        )

        assert result == ("first", "second")

    def test_should_flatten_nested_groups_when_groups_have_children(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first", "second"],
                "first": ["alpha", "beta"],
                "second": ["gamma", "delta"],
            },
        )

        assert result == ("alpha", "beta", "gamma", "delta")

    def test_should_flatten_deeply_nested_groups_when_groups_are_nested(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first"],
                "first": ["second"],
                "second": ["third"],
                "third": ["fourth"],
                "fourth": ["leaf"],
            },
        )

        assert result == ("leaf",)

    def test_should_preserve_child_order_when_groups_are_flattened(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["third", "first", "second"],
                "first": ["alpha", "beta"],
                "second": ["gamma"],
                "third": ["delta"],
            },
        )

        assert result == ("delta", "alpha", "beta", "gamma")

    def test_should_return_unresolved_target_when_group_is_missing(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "unknown",
            {"root": ["first", "second"]},
        )

        assert result == ("unknown",)

    def test_should_return_empty_tuple_when_group_has_no_children(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {"root": []},
        )

        assert result == ()

    def test_should_remove_duplicate_values_when_groups_overlap(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first", "second"],
                "first": ["shared", "alpha"],
                "second": ["shared", "beta"],
            },
        )

        assert result == ("shared", "alpha", "beta")

    def test_should_remove_duplicate_values_when_group_references_itself(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["root", "first"],
                "first": ["second"],
            },
        )

        assert result == ("second",)

    def test_should_terminate_when_groups_contain_circular_references(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first"],
                "first": ["second"],
                "second": ["root", "third"],
                "third": ["first", "leaf"],
            },
        )

        assert result == ("leaf",)

    def test_should_preserve_unresolved_values_when_nested_groups_are_missing(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first", "missing"],
                "first": ["leaf"],
            },
        )

        assert result == ("leaf", "missing")

    def test_should_flatten_groups_with_tuple_children(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ("first", "second"),
                "first": ("alpha", "beta"),
            },
        )

        assert result == ("alpha", "beta", "second")

    def test_should_flatten_groups_with_unicode_values(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "根",
            {
                "根": ["第一", "第二"],
                "第一": ["子項目"],
            },
        )

        assert result == ("子項目", "第二")

    def test_should_flatten_groups_with_special_characters(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first-value", "second/value"],
                "first-value": ["item@123"],
            },
        )

        assert result == ("item@123", "second/value")

    def test_should_deduplicate_zero_and_false_as_equal_values(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {"root": [0, False]},
        )

        assert result == (0,)

    def test_should_raise_value_error_when_target_is_none(
        self,
        manager,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="'target' must be defined",
        ):
            manager.flatten_group(None, {"root": ["first"]})

    @pytest.mark.parametrize(
        "target",
        [
            pytest.param("", id="empty-string"),
            pytest.param(0, id="zero"),
            pytest.param(False, id="false"),
        ],
    )
    def test_should_raise_value_error_when_target_is_falsey(
        self,
        manager,
        target,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="'target' must be defined",
        ):
            manager.flatten_group(
                target,
                {"root": ["first"]},
            )

    def test_should_raise_value_error_when_data_is_none(
        self,
        manager,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="'data' must be defined",
        ):
            manager.flatten_group("root", None)

    def test_should_raise_value_error_when_data_is_empty(
        self,
        manager,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="'data' must be defined",
        ):
            manager.flatten_group("root", {})

    def test_should_raise_type_error_when_target_is_unhashable(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.flatten_group(
                ["root"],
                {"root": ["first"]},
            )

    def test_should_raise_type_error_when_child_collection_is_none(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.flatten_group(
                "root",
                {"root": None},
            )

    def test_should_raise_type_error_when_data_is_not_mapping(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            ["first", "second"],
        )

        assert result == ("root",)

    def test_should_raise_type_error_when_leaf_is_unhashable(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.flatten_group(
                "root",
                {"root": [["first"]]},
            )

    def test_should_return_tuple_when_all_values_are_resolved(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first", "second"],
                "first": [],
                "second": [],
            },
        )

        assert isinstance(result, tuple)
        assert result == ()

    def test_should_accept_string_children_when_group_is_flattened(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {"root": "abc"},
        )

        assert result == ("a", "b", "c")

    def test_should_flatten_large_collection_when_many_children_exist(
        self,
        manager,
    ) -> None:
        children = tuple(
            f"child-{index}"
            for index in range(10000)
        )

        result = manager.flatten_group(
            "root",
            {"root": children},
        )

        assert len(result) == 10000
        assert result[0] == "child-0"
        assert result[-1] == "child-9999"

    def test_should_flatten_deep_groups_without_recursion_error(
        self,
        manager,
    ) -> None:
        data = {
            f"group-{index}": [f"group-{index + 1}"]
            for index in range(1000)
        }
        data["group-1000"] = ["leaf"]

        result = manager.flatten_group("group-0", data)

        assert result == ("leaf",)

    def test_should_handle_repeated_group_references_under_load(
        self,
        manager,
    ) -> None:
        data = {
            "root": ["first", "second", "third"],
            "first": ["shared", "alpha"],
            "second": ["shared", "beta"],
            "third": ["shared", "gamma"],
        }

        results = tuple(
            manager.flatten_group("root", data)
            for _ in range(1000)
        )

        assert all(result == results[0] for result in results)
        assert results[0] == (
            "shared",
            "alpha",
            "beta",
            "gamma",
        )

    def test_should_construct_and_shutdown_repeatedly_without_failure(
        self,
    ) -> None:
        manager_class = GroupSelectionManager()

        instances = tuple(
            manager_class()
            for _ in range(1000)
        )

        results = tuple(
            instance.shutdown()
            for instance in instances
        )

        assert len(instances) == 1000
        assert all(result is True for result in results)

    def test_should_preserve_input_data_when_groups_are_flattened(
        self,
        manager,
    ) -> None:
        data = {
            "root": ["first", "second"],
            "first": ["alpha", "beta"],
            "second": ["gamma"],
        }
        original = {
            key: list(value)
            for key, value in data.items()
        }

        manager.flatten_group("root", data)

        assert data == original

    def test_should_construct_when_instance_is_initialized(self) -> None:
        manager_class = GroupSelectionManager()
        construct = Mock(return_value=True)

        with patch.object(manager_class, "construct", construct):
            manager_class()

        construct.assert_called_once_with()

    def test_should_return_none_when_context_is_exited(
        self,
        manager,
    ) -> None:
        result = manager.__exit__(None, None, None)

        assert result is None

    def test_should_return_target_when_data_is_sequence_without_target_key(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            ["first", "second"],
        )

        assert result == ("root",)

    def test_should_return_target_when_data_is_tuple_without_target_key(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            ("first", "second"),
        )

        assert result == ("root",)

    def test_should_flatten_groups_with_multiple_child_collection_types(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ("first", "second"),
                "first": ["alpha", "beta"],
                "second": ("gamma",),
            },
        )

        assert result == ("alpha", "beta", "gamma")

    def test_should_return_empty_tuple_when_all_children_are_groups(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first", "second"],
                "first": [],
                "second": [],
            },
        )

        assert result == ()

    def test_should_raise_type_error_when_nested_value_is_unhashable(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.flatten_group(
                "root",
                {
                    "root": ["first"],
                    "first": [["leaf"]],
                },
            )

    def test_should_preserve_order_when_duplicate_groups_are_referenced(
        self,
        manager,
    ) -> None:
        result = manager.flatten_group(
            "root",
            {
                "root": ["first", "second", "first"],
                "first": ["alpha", "beta"],
                "second": ["gamma"],
            },
        )

        assert result == ("alpha", "beta", "gamma")

    def test_should_not_modify_nested_input_collections_when_flattened(
        self,
        manager,
    ) -> None:
        data = {
            "root": ["first", "second"],
            "first": ["alpha", "beta"],
            "second": ["gamma"],
        }
        original = {
            key: value.copy()
            for key, value in data.items()
        }

        manager.flatten_group("root", data)

        assert data == original

