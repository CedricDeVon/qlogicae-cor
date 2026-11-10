
import json

import pytest

from qlogicae_cor.v3.library.value_cache_storage_manager import (
    ValueCacheStorageManager,
)


class TestValueCacheStorageManager:
    @pytest.fixture
    def manager(self):
        return ValueCacheStorageManager()()

    @pytest.fixture
    def populated_manager(self, manager):
        manager.values = {
            "root": {
                "value": 1,
                "nested": {
                    "answer": 42,
                },
                "list": [
                    {
                        "name": "zero",
                    },
                    {
                        "name": "one",
                    },
                ],
                "tuple": (
                    "a",
                    "b",
                ),
            },
            "items": [
                10,
                20,
                {
                    "value": 30,
                },
            ],
        }

        return manager

    def test_collection_should_initially_be_empty(self, manager):
        assert manager.values == {}
        assert manager.defaults == {}

    def test_values_setter_should_accept_dictionary(self, manager):
        values = {"value": 1}

        manager.values = values

        assert manager.values is values

    def test_values_setter_should_raise_for_invalid_type(self, manager):
        with pytest.raises(ValueError):
            manager.values = []

    def test_defaults_setter_should_accept_dictionary(self, manager):
        defaults = {"value": 1}

        manager.defaults = defaults

        assert manager.defaults is defaults

    def test_defaults_setter_should_raise_for_invalid_type(self, manager):
        with pytest.raises(ValueError):
            manager.defaults = []

    def test_setup_should_return_false_without_arguments(self, manager):
        with pytest.raises(ValueError):
            manager.setup()

    def test_setup_should_initialize_values_and_defaults(self, manager):
        values = {"value": 1}
        defaults = {"value": 2}

        assert manager.setup(
            values=values,
            defaults=defaults,
        )

        assert manager.values is values
        assert manager.defaults is defaults

    def test_setup_should_replace_none_with_empty_dictionaries(self, manager):
        assert manager.setup(
            values=None,
            defaults=None,
        )

        assert manager.values == {}
        assert manager.defaults == {}

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            (
                {"values": []},
                "'kwargs.values' must be a dictionary",
            ),
            (
                {"defaults": []},
                "'kwargs.defaults' must be a dictionary",
            ),
        ],
    )
    def test_setup_should_raise_for_invalid_cache_type(
        self,
        manager,
        kwargs,
        message,
    ):
        with pytest.raises(ValueError, match=message):
            manager.setup(**kwargs)

    @pytest.mark.parametrize(
        ("keys", "expected"),
        [
            ("root", ("root",)),
            (("root", "value"), ("root", "value")),
            (["root", "value"], ("root", "value")),
        ],
    )
    def test_normalize_keys(self, manager, keys, expected):
        assert manager._normalize_keys(keys=keys) == expected

    @pytest.mark.parametrize(
        "keys",
        [
            [],
            (),
            None,
            1,
            {},
        ],
    )
    def test_normalize_keys_should_raise_for_invalid_keys(
        self,
        manager,
        keys,
    ):
        with pytest.raises(ValueError):
            manager._normalize_keys(keys=keys)

    @pytest.mark.parametrize(
        ("typename", "expected"),
        [
            ("values", "values"),
            ("defaults", "defaults"),
        ],
    )
    def test_normalize_typename(self, manager, typename, expected):
        assert manager._normalize_typename(
            typename=typename,
        ) == expected

    def test_normalize_typename_should_raise_for_invalid_type(
        self,
        manager,
    ):
        with pytest.raises(ValueError):
            manager._normalize_typename(typename="invalid")

    def test_read_specified_values_cache(self, populated_manager):
        assert populated_manager.read_specified_cache(
            typename="values",
        ) is populated_manager.values

    def test_read_specified_defaults_cache(self, populated_manager):
        assert populated_manager.read_specified_cache(
            typename="defaults",
        ) is populated_manager.defaults

    @pytest.mark.parametrize(
        ("keys", "expected"),
        [
            (["root"], True),
            (["root", "value"], True),
            (["root", "nested", "answer"], True),
            (["root", "list", 0], True),
            (["root", "list", 1, "name"], True),
            (["items", 2, "value"], True),
            (["root", "missing"], False),
            (["missing"], False),
            (["items", 10], False),
            (["items", -1], False),
            (["items", "0"], False),
            (["root", "value", "child"], False),
            (["root", "tuple", 1], True),
        ],
    )
    def test_is_key_item_found(
        self,
        populated_manager,
        keys,
        expected,
    ):
        assert populated_manager.is_key_item_found(
            keys=keys,
        ) is expected

    @pytest.mark.parametrize(
        ("keys", "expected"),
        [
            ("root", {
                "value": 1,
                "nested": {
                    "answer": 42,
                },
                "list": [
                    {"name": "zero"},
                    {"name": "one"},
                ],
                "tuple": ("a", "b"),
            }),
            (["root", "value"], 1),
            (["root", "nested", "answer"], 42),
            (["root", "list", 0, "name"], "zero"),
            (["root", "list", 1], {"name": "one"}),
            (["items", 2, "value"], 30),
            (["root", "missing"], None),
            (["missing"], None),
            (["items", -1], None),
            (["items", 99], None),
            (["items", "0"], None),
            (["root", "value", "child"], None),
            (["root", "tuple", 0], "a"),
        ],
    )
    def test_get_one_item(
        self,
        populated_manager,
        keys,
        expected,
    ):
        assert populated_manager.get_one_item(
            keys=keys,
        ) == expected

    def test_get_one_item_should_return_none_for_empty_keys(self, manager):
        with pytest.raises(ValueError):
            manager.get_one_item(keys=[])

    def test_get_one_item_should_support_tuple_keys(self, populated_manager):
        assert populated_manager.get_one_item(
            keys=("root", "value"),
        ) == 1

    def test_get_one_item_should_use_defaults_when_value_is_missing(
        self,
        manager,
    ):
        manager.defaults = {
            "root": {
                "value": 42,
            },
        }

        assert manager.get_one_item(
            keys=["root", "value"],
        ) == 42

    def test_get_one_item_should_fallback_to_defaults_for_missing_nested_key(
        self,
        manager,
    ):
        manager.values = {
            "root": {
                "existing": 1,
            },
        }

        manager.defaults = {
            "root": {
                "existing": 2,
                "missing": 42,
            },
        }

        assert manager.get_one_item(
            keys=["root", "missing"],
        ) == 42

    def test_is_key_item_found_should_use_defaults_fallback(self, manager):
        manager.defaults = {
            "root": {
                "value": 42,
            },
        }

        assert manager.is_key_item_found(
            keys=["root", "value"],
        ) is True

    def test_defaults_typename_should_not_fallback_to_values(self, manager):
        manager.values = {"value": 1}
        manager.defaults = {}

        assert manager.is_key_item_found(
            keys="value",
            typename="defaults",
        ) is False

        assert manager.get_one_item(
            keys="value",
            typename="defaults",
        ) is None

    def test_get_parent_should_return_dictionary_parent(
        self,
        populated_manager,
    ):
        parent, key = populated_manager._get_parent(
            keys=["root", "value"],
        )

        assert parent is populated_manager.values["root"]
        assert key == "value"

    def test_get_parent_should_create_missing_intermediate_dictionary(
        self,
        manager,
    ):
        parent, key = manager._get_parent(
            keys=["a", "b", "c"],
        )

        assert parent == {}
        assert key == "c"
        assert manager.values == {
            "a": {
                "b": {},
            },
        }

    def test_get_parent_should_not_create_missing_path_when_disabled(
        self,
        manager,
    ):
        parent, key = manager._get_parent(
            keys=["missing", "child"],
            create_missing=False,
        )

        assert parent is None
        assert key is None
        assert manager.values == {}

    def test_get_parent_should_return_none_when_traversing_scalar(
        self,
        manager,
    ):
        manager.values["value"] = 1

        parent, key = manager._get_parent(
            keys=["value", "child"],
        )

        assert parent is None
        assert key is None

    def test_get_parent_should_support_nested_list(self, populated_manager):
        parent, key = populated_manager._get_parent(
            keys=["items", 2, "value"],
        )

        assert parent is populated_manager.values["items"][2]
        assert key == "value"

    def test_get_parent_should_raise_for_invalid_list_key_type(
        self,
        populated_manager,
    ):
        with pytest.raises(TypeError):
            populated_manager._get_parent(
                keys=["items", "invalid", "value"],
            )

    def test_get_parent_should_raise_for_invalid_list_index(
        self,
        populated_manager,
    ):
        with pytest.raises(IndexError):
            populated_manager._get_parent(
                keys=["items", 10, "value"],
            )

    def test_set_one_item_should_create_missing_path(self, manager):
        assert manager.set_one_item(
            keys=["a", "b", "c"],
            value=100,
        )

        assert manager.values == {
            "a": {
                "b": {
                    "c": 100,
                },
            },
        }

    def test_set_one_item_should_update_existing_dictionary_item(
        self,
        populated_manager,
    ):
        assert populated_manager.set_one_item(
            keys=["root", "value"],
            value=999,
        )

        assert populated_manager.values["root"]["value"] == 999

    def test_set_one_item_should_update_existing_list_item(
        self,
        populated_manager,
    ):
        assert populated_manager.set_one_item(
            keys=["items", 1],
            value=999,
        )

        assert populated_manager.values["items"][1] == 999

    def test_set_one_item_should_update_nested_dictionary_inside_list(
        self,
        populated_manager,
    ):
        assert populated_manager.set_one_item(
            keys=["items", 2, "value"],
            value=123,
        )

        assert populated_manager.values["items"][2]["value"] == 123

    def test_set_one_item_should_raise_for_empty_keys(self, manager):
        with pytest.raises(ValueError):
            manager.set_one_item(
                keys=[],
                value=1,
            )

    def test_set_one_item_should_return_false_when_create_missing_is_disabled(
        self,
        manager,
    ):
        assert manager.set_one_item(
            keys=["missing", "child"],
            value=1,
            create_missing=False,
        ) is False

        assert manager.values == {}

    def test_set_one_item_should_return_false_when_traversing_scalar(
        self,
        manager,
    ):
        manager.values["value"] = 1

        assert manager.set_one_item(
            keys=["value", "child"],
            value=2,
        ) is False

        assert manager.values["value"] == 1

    def test_set_one_item_should_raise_for_invalid_list_index(
        self,
        populated_manager,
    ):
        with pytest.raises(IndexError):
            populated_manager.set_one_item(
                keys=["items", 10, "child"],
                value=1,
            )

    def test_set_one_item_should_raise_for_invalid_destination_list_key_type(
        self,
        populated_manager,
    ):
        with pytest.raises(TypeError):
            populated_manager.set_one_item(
                keys=["items", "invalid"],
                value=1,
            )

    def test_set_one_item_should_raise_for_invalid_destination_list_index(
        self,
        populated_manager,
    ):
        with pytest.raises(IndexError):
            populated_manager.set_one_item(
                keys=["items", 999],
                value=1,
            )

    def test_set_one_item_should_update_nested_list(self, manager):
        manager.values["items"] = [
            {
                "values": [
                    1,
                    2,
                ],
            },
        ]

        assert manager.set_one_item(
            keys=["items", 0, "values", 1],
            value=100,
        )

        assert manager.values["items"][0]["values"][1] == 100

    def test_set_one_item_should_raise_for_nested_list_invalid_key_type(
        self,
        manager,
    ):
        manager.values["items"] = [
            {
                "values": [1, 2],
            },
        ]

        with pytest.raises(TypeError):
            manager.set_one_item(
                keys=["items", 0, "values", "1"],
                value=100,
            )

    def test_set_one_item_should_raise_for_nested_list_index_out_of_range(
        self,
        manager,
    ):
        manager.values["items"] = [
            {
                "values": [1, 2],
            },
        ]

        with pytest.raises(IndexError):
            manager.set_one_item(
                keys=["items", 0, "values", 10],
                value=100,
            )

    def test_set_one_item_should_return_false_when_destination_is_tuple(
        self,
        manager,
    ):
        manager.values["tuple"] = (1, 2)

        assert manager.set_one_item(
            keys=["tuple", 0],
            value=3,
        ) is False

        assert manager.values["tuple"] == (1, 2)

    def test_set_one_item_should_support_defaults_cache(self, manager):
        assert manager.set_one_item(
            keys=["root", "value"],
            value=42,
            typename="defaults",
        )

        assert manager.defaults == {
            "root": {
                "value": 42,
            },
        }

        assert manager.values == {}

    def test_remove_one_item_should_remove_dictionary_key(
        self,
        populated_manager,
    ):
        assert populated_manager.remove_one_item(
            keys=["root", "value"],
        ) is True

        assert "value" not in populated_manager.values["root"]

    def test_remove_one_item_should_remove_list_item(
        self,
        populated_manager,
    ):
        assert populated_manager.remove_one_item(
            keys=["items", 1],
        ) is True

        assert populated_manager.values["items"] == [
            10,
            {
                "value": 30,
            },
        ]

    def test_remove_one_item_should_return_false_for_empty_parent(
        self,
        manager,
    ):
        assert manager.remove_one_item(
            keys=["missing", "value"],
        ) is False

        assert manager.values == {}

    def test_remove_one_item_should_return_false_for_missing_key(
        self,
        populated_manager,
    ):
        assert populated_manager.remove_one_item(
            keys=["root", "missing"],
        ) is False

    def test_remove_one_item_should_raise_for_empty_keys(self, manager):
        with pytest.raises(ValueError):
            manager.remove_one_item(keys=[])

    def test_remove_one_item_should_return_false_for_invalid_list_index(
        self,
        populated_manager,
    ):
        assert populated_manager.remove_one_item(
            keys=["items", 100],
        ) is False

    def test_remove_one_item_should_return_false_when_traversing_scalar(
        self,
        manager,
    ):
        manager.values["value"] = 1

        assert manager.remove_one_item(
            keys=["value", "child"],
        ) is False

    def test_remove_one_item_should_return_false_when_destination_is_tuple(
        self,
        manager,
    ):
        manager.values["tuple"] = (1, 2)

        assert manager.remove_one_item(
            keys=["tuple", 0],
        ) is False

    def test_remove_one_item_should_remove_from_defaults(self, manager):
        manager.defaults = {
            "root": {
                "value": 42,
            },
        }

        assert manager.remove_one_item(
            keys=["root", "value"],
            typename="defaults",
        )

        assert manager.defaults == {
            "root": {},
        }

    def test_remove_all_items_should_clear_values(self, populated_manager):
        assert populated_manager.remove_all_items()

        assert populated_manager.values == {}

    def test_remove_all_items_should_clear_defaults(self, manager):
        manager.defaults = {
            "root": {
                "value": 42,
            },
        }

        assert manager.remove_all_items(
            typename="defaults",
        )

        assert manager.defaults == {}

    def test_remove_all_items_should_preserve_other_cache(self, manager):
        manager.values = {"value": 1}
        manager.defaults = {"value": 2}

        assert manager.remove_all_items()

        assert manager.values == {}
        assert manager.defaults == {"value": 2}

    def test_display_one_item(
        self,
        populated_manager,
        capsys,
    ):
        assert populated_manager.display_one_item(
            keys=["root"],
        )

        output = capsys.readouterr().out

        assert output == (
            json.dumps(
                populated_manager.values["root"],
                indent=2,
                sort_keys=False,
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )

    def test_display_one_item_should_return_false_for_missing_key(
        self,
        manager,
    ):
        assert manager.display_one_item(
            keys=["missing"],
        ) is False

    def test_display_one_item_should_display_defaults_fallback(
        self,
        manager,
        capsys,
    ):
        manager.defaults = {
            "root": {
                "value": 42,
            },
        }

        assert manager.display_one_item(
            keys=["root"],
        )

        assert json.loads(
            capsys.readouterr().out,
        ) == {
            "value": 42,
        }

    def test_display_all_items(
        self,
        populated_manager,
        capsys,
    ):
        assert populated_manager.display_all_items()

        output = capsys.readouterr().out

        assert output == (
            json.dumps(
                populated_manager.values,
                indent=2,
                sort_keys=False,
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )

    def test_display_all_defaults(
        self,
        manager,
        capsys,
    ):
        manager.defaults = {
            "root": {
                "value": 42,
            },
        }

        assert manager.display_all_items(
            typename="defaults",
        )

        assert json.loads(
            capsys.readouterr().out,
        ) == {
            "root": {
                "value": 42,
            },
        }

    def test_construct_should_initialize_empty_caches(self):
        manager = ValueCacheStorageManager()()

        assert manager.values == {}
        assert manager.defaults == {}

    def test_shutdown_should_return_true(self, manager):
        assert manager.shutdown() is True

    def test_context_manager_should_return_manager(self):
        manager = ValueCacheStorageManager()()

        with manager as context:
            assert context is manager

from unittest.mock import patch


class TestValueCacheStorageManagerAdditional:
    @pytest.fixture
    def manager_class(self):
        manager_class = ValueCacheStorageManager()
        manager_class._singleton = None
        return manager_class

    @pytest.fixture
    def manager(self):
        return ValueCacheStorageManager()()

    def test_factory_should_return_same_class_after_allocation(self):
        first = ValueCacheStorageManager()
        second = ValueCacheStorageManager()

        assert first is second

    def test_get_singleton_should_return_same_instance(self, manager_class):
        first = manager_class.get_singleton()
        second = manager_class.get_singleton()

        assert first is second

    def test_get_singleton_should_initialize_only_once(self, manager_class):
        first = manager_class.get_singleton()

        second = manager_class.get_singleton()

        assert first is second
        assert first.values == {}

    def test_context_manager_should_call_shutdown(self, manager):
        with patch.object(
            type(manager),
            "shutdown",
            return_value=True,
        ) as shutdown:
            with manager:
                pass

        shutdown.assert_called_once_with()

    def test_context_manager_should_not_suppress_exceptions(self, manager):
        with pytest.raises(RuntimeError, match="test"):
            with manager:
                raise RuntimeError("test")

    def test_setup_should_reset_defaults_when_only_values_are_provided(
        self,
        manager,
    ):
        manager.defaults = {"existing": 1}

        assert manager.setup(values={"new": 2}) is True

        assert manager.values == {"new": 2}
        assert manager.defaults == {}

    def test_setup_should_reset_values_when_only_defaults_are_provided(
        self,
        manager,
    ):
        manager.values = {"existing": 1}

        assert manager.setup(defaults={"new": 2}) is True

        assert manager.values == {}
        assert manager.defaults == {"new": 2}

    def test_setup_should_accept_unrecognized_arguments(self, manager):
        assert manager.setup(unrecognized=True) is True

        assert manager.values == {}
        assert manager.defaults == {}

    def test_setup_should_replace_existing_caches(self, manager):
        manager.values = {"existing": 1}
        manager.defaults = {"existing": 2}

        values = {"new": 3}
        defaults = {"new": 4}

        assert manager.setup(
            values=values,
            defaults=defaults,
        ) is True

        assert manager.values is values
        assert manager.defaults is defaults

    def test_normalize_typename_should_default_to_values(self, manager):
        assert manager._normalize_typename() == "values"

    def test_read_specified_cache_should_default_to_values(self, manager):
        manager.values = {"value": 1}

        assert manager.read_specified_cache() is manager.values

    def test_get_item_from_cache_should_return_true_for_empty_path(
        self,
        manager,
    ):
        manager.values = {"value": 1}

        found, item = manager._get_item_from_cache(
            keys=(),
            typename="values",
        )

        assert found is True
        assert item is manager.values

    def test_get_item_from_cache_should_return_false_for_unsupported_key(
        self,
        manager,
    ):
        manager.values = {"value": 1}

        found, item = manager._get_item_from_cache(
            keys=["value", "child"],
            typename="values",
        )

        assert found is False
        assert item is None

    def test_get_item_from_cache_should_return_false_for_invalid_list_key(
        self,
        manager,
    ):
        manager.values = {"items": [1, 2]}

        found, item = manager._get_item_from_cache(
            keys=["items", "invalid"],
            typename="values",
        )

        assert found is False
        assert item is None

    def test_get_one_item_should_prioritize_values_over_defaults(
        self,
        manager,
    ):
        manager.values = {
            "root": {
                "value": 1,
            },
        }

        manager.defaults = {
            "root": {
                "value": 2,
            },
        }

        assert manager.get_one_item(
            keys=["root", "value"],
        ) == 1

    def test_is_key_item_found_should_return_true_for_none_value(
        self,
        manager,
    ):
        manager.values = {"value": None}

        assert manager.is_key_item_found(
            keys="value",
        ) is True

        assert manager.get_one_item(
            keys="value",
        ) is None

    def test_get_one_item_should_support_nested_tuple(self, manager):
        manager.values = {
            "root": {
                "tuple": ("first", "second"),
            },
        }

        assert manager.get_one_item(
            keys=["root", "tuple", 1],
        ) == "second"

    def test_get_parent_should_return_parent_for_single_key(self, manager):
        parent, key = manager._get_parent(
            keys=["value"],
        )

        assert parent is manager.values
        assert key == "value"

    def test_get_parent_should_not_traverse_nested_tuple(self, manager):
        manager.values = {
            "root": {
                "tuple": ("first", "second"),
            },
        }

        parent, key = manager._get_parent(
            keys=["root", "tuple", 0],
        )

        assert parent is None
        assert key is None

    def test_get_parent_should_raise_for_negative_list_index(
        self,
        manager,
    ):
        manager.values = {"items": [1, 2]}

        with pytest.raises(IndexError):
            manager._get_parent(
                keys=["items", -1, "value"],
            )

    def test_set_one_item_should_set_single_key(self, manager):
        assert manager.set_one_item(
            keys=["value"],
            value=42,
        ) is True

        assert manager.values == {"value": 42}

    def test_set_one_item_should_raise_for_negative_destination_index(
        self,
        manager,
    ):
        manager.values = {"items": [1, 2]}

        with pytest.raises(IndexError):
            manager.set_one_item(
                keys=["items", -1],
                value=3,
            )

    def test_set_one_item_should_raise_for_invalid_destination_list_key_type(
        self,
        manager,
    ):
        manager.values = {"items": [1, 2]}

        with pytest.raises(TypeError):
            manager.set_one_item(
                keys=["items", "invalid"],
                value=3,
            )

    def test_set_one_item_should_raise_for_nested_list_invalid_key_type(
        self,
        manager,
    ):
        manager.values = {
            "items": [
                {
                    "values": [1, 2],
                },
            ],
        }

        with pytest.raises(TypeError):
            manager.set_one_item(
                keys=["items", 0, "values", "1"],
                value=100,
            )

    def test_set_one_item_should_raise_for_nested_list_index_out_of_range(
        self,
        manager,
    ):
        manager.values = {
            "items": [
                {
                    "values": [1, 2],
                },
            ],
        }

        with pytest.raises(IndexError):
            manager.set_one_item(
                keys=["items", 0, "values", 10],
                value=100,
            )

    def test_set_one_item_should_not_modify_nested_tuple(self, manager):
        manager.values = {
            "root": {
                "tuple": ("first", "second"),
            },
        }

        assert manager.set_one_item(
            keys=["root", "tuple", 0],
            value="updated",
        ) is False

        assert manager.values["root"]["tuple"] == (
            "first",
            "second",
        )

    def test_remove_one_item_should_raise_for_invalid_list_key_type(
        self,
        manager,
    ):
        manager.values = {"items": [1, 2]}

        with pytest.raises(TypeError):
            manager.remove_one_item(
                keys=["items", "invalid"],
            )

    def test_remove_one_item_should_return_false_for_negative_list_index(
        self,
        manager,
    ):
        manager.values = {"items": [1, 2]}

        assert manager.remove_one_item(
            keys=["items", -1],
        ) is False

        assert manager.values["items"] == [1, 2]

    def test_remove_one_item_should_remove_single_key(self, manager):
        manager.values = {"value": 42}

        assert manager.remove_one_item(
            keys=["value"],
        ) is True

        assert manager.values == {}

    def test_remove_one_item_should_not_modify_nested_tuple(self, manager):
        manager.values = {
            "root": {
                "tuple": ("first", "second"),
            },
        }

        assert manager.remove_one_item(
            keys=["root", "tuple", 0],
        ) is False

        assert manager.values["root"]["tuple"] == (
            "first",
            "second",
        )

    def test_remove_all_items_should_preserve_cache_identity(self, manager):
        values = {"value": 1}
        defaults = {"value": 2}

        manager.values = values
        manager.defaults = defaults

        assert manager.remove_all_items() is True

        assert manager.values is values
        assert manager.defaults is defaults
        assert values == {}
        assert defaults == {"value": 2}

    def test_display_all_items_should_preserve_unicode(
        self,
        manager,
        capsys,
    ):
        manager.values = {"message": "こんにちは"}

        assert manager.display_all_items() is True

        assert "こんにちは" in capsys.readouterr().out

    def test_display_all_items_should_convert_unsupported_objects(
        self,
        manager,
        capsys,
    ):
        manager.values = {"value": object()}

        assert manager.display_all_items() is True

        output = json.loads(capsys.readouterr().out)

        assert isinstance(output["value"], str)

    def test_display_one_item_should_preserve_unicode(
        self,
        manager,
        capsys,
    ):
        manager.values = {"message": "こんにちは"}

        assert manager.display_one_item(
            keys="message",
        ) is True

        assert capsys.readouterr().out == '"こんにちは"\n'

    def test_display_one_item_should_convert_unsupported_objects(
        self,
        manager,
        capsys,
    ):
        manager.values = {"value": object()}

        assert manager.display_one_item(
            keys="value",
        ) is True

        output = json.loads(capsys.readouterr().out)

        assert isinstance(output, str)

    def test_get_parent_should_return_none_for_unsupported_root_container(
        self,
        manager,
    ):
        manager._values = ("first", "second")

        parent, key = manager._get_parent(
            keys=["root", "child"],
        )

        assert parent is None
        assert key is None


    def test_set_one_item_should_return_false_for_unsupported_root_container(
        self,
        manager,
    ):
        manager._values = ("first", "second")

        assert manager.set_one_item(
            keys=["value"],
            value=1,
        ) is False

        assert manager._values == ("first", "second")


    def test_remove_one_item_should_return_false_for_unsupported_root_container(
        self,
        manager,
    ):
        manager._values = ("first", "second")

        assert manager.remove_one_item(
            keys=["value"],
        ) is False

        assert manager._values == ("first", "second")


    