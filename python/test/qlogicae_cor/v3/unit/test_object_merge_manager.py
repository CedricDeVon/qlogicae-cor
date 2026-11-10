from copy import deepcopy

import pytest

from qlogicae_cor.v3.library.object_merge_manager import ObjectMergeManager


class TestObjectMergeManager:
    @pytest.fixture
    def manager(self):
        return ObjectMergeManager()()

    def test_handle_deep_merging_should_return_deepcopy_of_right_when_left_is_none(
        self,
        manager,
    ) -> None:
        right = {"a": {"b": [1, 2]}}

        result = manager.deep_merge(None, right)

        assert result == right
        assert result is not right
        assert result["a"] is not right["a"]
        assert result["a"]["b"] is not right["a"]["b"]

    def test_handle_deep_merging_should_return_deepcopy_of_left_when_right_is_none(
        self,
        manager,
    ) -> None:
        left = {"a": {"b": [1, 2]}}

        result = manager.deep_merge(left, None)

        assert result == left
        assert result is not left
        assert result["a"] is not left["a"]
        assert result["a"]["b"] is not left["a"]["b"]

    def test_handle_deep_merging_should_merge_nested_dictionaries(
        self,
        manager,
    ) -> None:
        left = {
            "a": {
                "b": 1,
                "c": 2,
            },
            "d": 3,
        }

        right = {
            "a": {
                "c": 4,
                "e": 5,
            },
            "f": 6,
        }

        result = manager.deep_merge(left, right)

        assert result == {
            "a": {
                "b": 1,
                "c": 4,
                "e": 5,
            },
            "d": 3,
            "f": 6,
        }

    def test_handle_deep_merging_should_concatenate_nested_lists(
        self,
        manager,
    ) -> None:
        left = {
            "a": [1, 2],
        }

        right = {
            "a": [3, 4],
        }

        result = manager.deep_merge(left, right)

        assert result == {
            "a": [1, 2, 3, 4],
        }

    def test_handle_deep_merging_should_replace_mixed_nested_types(
        self,
        manager,
    ) -> None:
        left = {
            "a": [1, 2],
            "b": {"x": 1},
        }

        right = {
            "a": {"value": 1},
            "b": [3, 4],
        }

        result = manager.deep_merge(left, right)

        assert result == {
            "a": {"value": 1},
            "b": [3, 4],
        }

    @pytest.mark.parametrize(
        ("left", "right", "expected"),
        [
            (1, 2, 2),
            ("a", "b", "b"),
            (True, False, False),
            (1.5, 2.5, 2.5),
            ({}, [], []),
            ([], {}, {}),
        ],
    )
    def test_handle_deep_merging_should_replace_non_mergeable_values(
        self,
        manager,
        left,
        right,
        expected,
    ) -> None:
        assert manager.deep_merge(left, right) == expected

    def test_handle_deep_merging_should_handle_deeply_nested_dictionaries(
        self,
        manager,
    ) -> None:
        left = {
            "a": {
                "b": {
                    "c": {
                        "d": 1,
                    },
                },
            },
        }

        right = {
            "a": {
                "b": {
                    "c": {
                        "e": 2,
                    },
                },
            },
        }

        result = manager.deep_merge(left, right)

        assert result == {
            "a": {
                "b": {
                    "c": {
                        "d": 1,
                        "e": 2,
                    },
                },
            },
        }

    def test_handle_deep_merging_should_not_mutate_inputs_or_share_references(
        self,
        manager,
    ) -> None:
        left = {
            "a": {
                "b": [1, 2],
            },
        }

        right = {
            "a": {
                "b": [3],
            },
        }

        left_copy = deepcopy(left)
        right_copy = deepcopy(right)

        result = manager.deep_merge(left, right)

        result["a"]["b"].append(999)

        assert left == left_copy
        assert right == right_copy

    @pytest.mark.parametrize(
        ("left", "right", "expected"),
        [
            ({}, {}, {}),
            ({}, {"a": 1}, {"a": 1}),
            ({"a": 1}, {}, {"a": 1}),
            ([], [], []),
            ([], [1], [1]),
            ([1], [], [1]),
        ],
    )
    def test_handle_deep_merging_should_handle_edge_cases(
        self,
        manager,
        left,
        right,
        expected,
    ) -> None:
        assert manager.deep_merge(left, right) == expected

    def test_handle_deep_merge_fragments_should_return_deepcopy_of_right_when_left_is_none(
        self,
        manager,
    ) -> None:
        right = {"a": {"b": [1, 2]}}

        result = manager.deep_merge_fragments(None, right)

        assert result == right
        assert result is not right
        assert result["a"] is not right["a"]
        assert result["a"]["b"] is not right["a"]["b"]

    def test_handle_deep_merge_fragments_should_return_deepcopy_of_left_when_right_is_none(
        self,
        manager,
    ) -> None:
        left = {"a": {"b": [1, 2]}}

        result = manager.deep_merge_fragments(left, None)

        assert result == left
        assert result is not left
        assert result["a"] is not left["a"]
        assert result["a"]["b"] is not left["a"]["b"]

    def test_handle_deep_merge_fragments_should_merge_nested_dictionaries(
        self,
        manager,
    ) -> None:
        left = {
            "a": {
                "b": 1,
                "c": 2,
            },
            "d": 3,
        }

        right = {
            "a": {
                "c": 4,
                "e": 5,
            },
            "f": 6,
        }

        result = manager.deep_merge_fragments(left, right)

        assert result == {
            "a": {
                "b": 1,
                "c": 4,
                "e": 5,
            },
            "d": 3,
            "f": 6,
        }

    def test_handle_deep_merge_fragments_should_replace_nested_lists(
        self,
        manager,
    ) -> None:
        left = {
            "a": [1, 2],
        }

        right = {
            "a": [3, 4],
        }

        result = manager.deep_merge_fragments(left, right)

        assert result == {
            "a": [3, 4],
        }

    def test_handle_deep_merge_fragments_should_replace_mixed_nested_types(
        self,
        manager,
    ) -> None:
        left = {
            "a": [1, 2],
            "b": {"x": 1},
        }

        right = {
            "a": {"value": 1},
            "b": [3, 4],
        }

        result = manager.deep_merge_fragments(left, right)

        assert result == {
            "a": {"value": 1},
            "b": [3, 4],
        }

    @pytest.mark.parametrize(
        ("left", "right", "expected"),
        [
            (1, 2, 2),
            ("a", "b", "b"),
            (True, False, False),
            (1.5, 2.5, 2.5),
            ({}, [], []),
            ([], {}, {}),
        ],
    )
    def test_handle_deep_merge_fragments_should_replace_non_mergeable_values(
        self,
        manager,
        left,
        right,
        expected,
    ) -> None:
        assert manager.deep_merge_fragments(left, right) == expected

    def test_handle_deep_merge_fragments_should_handle_deeply_nested_dictionaries(
        self,
        manager,
    ) -> None:
        left = {
            "a": {
                "b": {
                    "c": {
                        "d": 1,
                    },
                },
            },
        }

        right = {
            "a": {
                "b": {
                    "c": {
                        "e": 2,
                    },
                },
            },
        }

        result = manager.deep_merge_fragments(left, right)

        assert result == {
            "a": {
                "b": {
                    "c": {
                        "d": 1,
                        "e": 2,
                    },
                },
            },
        }

    def test_handle_deep_merge_fragments_should_not_mutate_inputs_or_share_references(
        self,
        manager,
    ) -> None:
        left = {
            "a": {
                "b": [1, 2],
            },
        }

        right = {
            "a": {
                "b": [3],
            },
        }

        left_copy = deepcopy(left)
        right_copy = deepcopy(right)

        result = manager.deep_merge_fragments(left, right)

        result["a"]["b"].append(999)

        assert left == left_copy
        assert right == right_copy

    @pytest.mark.parametrize(
        ("left", "right", "expected"),
        [
            ({}, {}, {}),
            ({}, {"a": 1}, {"a": 1}),
            ({"a": 1}, {}, {"a": 1}),
            ([], [], []),
            ([], [1], [1]),
            ([1], [], []),
        ],
    )

    def test_handle_deep_merge_fragments_should_handle_edge_cases(
        self,
        manager,
        left,
        right,
        expected,
    ) -> None:
        assert manager.deep_merge_fragments(left, right) == expected

    def test_handle_context_manager_should_return_manager_instance(
        self,
    ) -> None:
        manager = ObjectMergeManager()()

        with manager as result:
            assert result is manager

    def test_handle_context_manager_should_shutdown_manager_on_exit(
        self,
    ) -> None:
        manager = ObjectMergeManager()()

        with manager as result:
            assert result is manager

    def test_handle_singleton_should_return_same_instance(
        self,
    ) -> None:
        manager_class = ObjectMergeManager()

        first = manager_class.get_singleton()
        second = manager_class.get_singleton()

        assert first is second

    def test_handle_singleton_should_initialize_instance_when_uninitialized(
        self,
    ) -> None:
        manager_class = ObjectMergeManager()
        manager_class._singleton = None

        manager = manager_class.get_singleton()

        assert isinstance(manager, manager_class)
        assert manager_class._singleton is manager

    def test_handle_setup_should_return_false_when_kwargs_are_empty(
        self,
        manager,
    ) -> None:
        with pytest.raises(ValueError):
            manager.setup()

    def test_handle_setup_should_return_true_when_kwargs_are_provided(
        self,
        manager,
    ) -> None:
        assert manager.setup(value=1) is True

    def test_handle_shutdown_should_return_true(
        self,
        manager,
    ) -> None:
        assert manager.shutdown() is True

    def test_handle_deep_merge_fragments_should_replace_empty_left_list(
        self,
        manager,
    ) -> None:
        assert manager.deep_merge_fragments([], [1, 2]) == [1, 2]

    def test_handle_deep_merge_fragments_should_replace_non_empty_left_list_with_empty_right_list(
        self,
        manager,
    ) -> None:
        assert manager.deep_merge_fragments([1, 2], []) == []

    def test_handle_deep_merge_fragments_should_preserve_nested_right_list(
        self,
        manager,
    ) -> None:
        left = {
            "a": {
                "b": [1, 2],
            },
        }

        right = {
            "a": {
                "b": [3, 4],
            },
        }

        result = manager.deep_merge_fragments(left, right)

        assert result == {
            "a": {
                "b": [3, 4],
            },
        }

    def test_handle_deep_merge_fragments_should_deepcopy_replaced_nested_list(
        self,
        manager,
    ) -> None:
        left = {
            "a": [1, 2],
        }

        right = {
            "a": [3, 4],
        }

        result = manager.deep_merge_fragments(left, right)

        result["a"].append(5)

        assert left["a"] == [1, 2]
        assert right["a"] == [3, 4]
        assert result["a"] is not right["a"]



