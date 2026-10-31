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


# from __future__ import annotations

# from copy import deepcopy

# import pytest


# def handle_deep_merging_recursive(
#     left: Any,
#     right: Any,
# ) -> Any:
#     if left is None:
#         return deepcopy(right)

#     if right is None:
#         return deepcopy(left)

#     if isinstance(left, dict) and isinstance(right, dict):
#         result = deepcopy(left)

#         for key, value in right.items():
#             if key in result:
#                 result[key] = handle_deep_merging_recursive(
#                     result[key],
#                     value,
#                 )
#             else:
#                 result[key] = deepcopy(value)

#         return result

#     if isinstance(left, list) and isinstance(right, list):
#         return deepcopy(left) + deepcopy(right)

#     return deepcopy(right)


# def handle_deep_merging_iterative(
#     left: Any,
#     right: Any,
# ) -> Any:
#     if left is None:
#         return deepcopy(right)

#     if right is None:
#         return deepcopy(left)

#     if not (isinstance(left, dict) and isinstance(right, dict)):
#         if isinstance(left, list) and isinstance(right, list):
#             return deepcopy(left) + deepcopy(right)

#         return deepcopy(right)

#     result = deepcopy(left)

#     stack: list[tuple[dict[str, Any], dict[str, Any]]] = [
#         (
#             result,
#             right,
#         ),
#     ]

#     while stack:
#         current_left, current_right = stack.pop()

#         for key, right_value in current_right.items():
#             if key not in current_left:
#                 current_left[key] = deepcopy(right_value)
#                 continue

#             left_value = current_left[key]

#             if isinstance(left_value, dict) and isinstance(right_value, dict):
#                 stack.append(
#                     (
#                         left_value,
#                         right_value,
#                     ),
#                 )

#             elif isinstance(left_value, list) and isinstance(right_value, list):
#                 current_left[key] = deepcopy(left_value) + deepcopy(right_value)

#             else:
#                 current_left[key] = deepcopy(
#                     right_value,
#                 )

#     return result


# def make_nested(
#     depth: int,
#     width: int,
# ):
#     if depth == 0:
#         return {f"item{i}": list(range(20)) for i in range(width)}

#     return {
#         f"level{i}": make_nested(
#             depth - 1,
#             width,
#         )
#         for i in range(width)
#     }


# @pytest.fixture(scope="session")
# def large_merge_data():
#     left = make_nested(
#         depth=5,
#         width=5,
#     )

#     right = make_nested(
#         depth=5,
#         width=5,
#     )

#     right["new"] = {
#         "hello": "world",
#     }

#     return left, right


# def test_recursive_large(
#     benchmark,
#     large_merge_data,
# ):
#     left, right = large_merge_data

#     benchmark(
#         handle_deep_merging_recursive,
#         deepcopy(left),
#         deepcopy(right),
#     )


# def test_iterative_large(
#     benchmark,
#     large_merge_data,
# ):
#     left, right = large_merge_data

#     benchmark(
#         handle_deep_merging_iterative,
#         deepcopy(left),
#         deepcopy(right),
#     )
