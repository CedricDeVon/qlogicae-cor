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
    def populated_manager(
        self,
        manager,
    ):
        manager.collection["root"] = {
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
        }

        manager.collection["items"] = [
            10,
            20,
            {
                "value": 30,
            },
        ]

        return manager

    def test_collection_should_initially_be_empty(
        self,
        manager,
    ) -> None:
        assert manager.collection == {}

    @pytest.mark.parametrize(
        ("keys", "expected"),
        [
            ([], False),
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
            (["root", "tuple", 5], False),
            (["root", "tuple", "1"], False),
        ],
    )
    def test_is_key_found(
        self,
        populated_manager,
        keys,
        expected,
    ) -> None:
        assert populated_manager.is_key_found(keys) is expected

    @pytest.mark.parametrize(
        ("keys", "expected"),
        [
            ([], None),
            (["root"], {
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
            }),
            (["root", "value"], 1),
            (["root", "nested", "answer"], 42),
            (["root", "list", 0, "name"], "zero"),
            (["root", "list", 1], {
                "name": "one",
            }),
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
    def test_get_one_value(
        self,
        populated_manager,
        keys,
        expected,
    ) -> None:
        assert populated_manager.get_one_value(keys) == expected

    def test_set_one_value_should_create_missing_path(
        self,
        manager,
    ) -> None:
        assert manager.set_one_value(
            ["a", "b", "c"],
            100,
        )

        assert manager.collection == {
            "a": {
                "b": {
                    "c": 100,
                },
            },
        }

    def test_set_one_value_should_update_existing_dictionary_value(
        self,
        populated_manager,
    ) -> None:
        assert populated_manager.set_one_value(
            ["root", "value"],
            999,
        )

        assert populated_manager.collection["root"]["value"] == 999

    def test_set_one_value_should_update_existing_list_value(
        self,
        populated_manager,
    ) -> None:
        assert populated_manager.set_one_value(
            ["items", 1],
            999,
        )

        assert populated_manager.collection["items"][1] == 999

    def test_set_one_value_should_update_nested_dictionary_inside_list(
        self,
        populated_manager,
    ) -> None:
        assert populated_manager.set_one_value(
            ["items", 2, "value"],
            123,
        )

        assert populated_manager.collection["items"][2]["value"] == 123

    def test_set_one_value_should_raise_for_empty_keys(
        self,
        manager,
    ) -> None:
        with pytest.raises(ValueError):
            manager.set_one_value([], 1)

    def test_set_one_value_should_raise_when_create_missing_is_false(
        self,
        manager,
    ) -> None:
        with pytest.raises(KeyError):
            manager.set_one_value(
                ["missing", "child"],
                1,
                create_missing=False,
            )

    def test_set_one_value_should_raise_when_traversing_scalar(
        self,
        manager,
    ) -> None:
        manager.collection["value"] = 1

        with pytest.raises(TypeError):
            manager.set_one_value(
                ["value", "child"],
                2,
            )

    def test_set_one_value_should_raise_for_invalid_list_key_type(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(TypeError):
            populated_manager.set_one_value(
                ["items", "0"],
                1,
            )

    def test_set_one_value_should_raise_for_invalid_list_index(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(IndexError):
            populated_manager.set_one_value(
                ["items", 10],
                1,
            )

    def test_remove_one_value_should_remove_dictionary_key(
        self,
        populated_manager,
    ) -> None:
        assert populated_manager.remove_one_value(
            ["root", "value"]
        ) is True

        assert "value" not in populated_manager.collection["root"]

    def test_remove_one_value_should_remove_list_item(
        self,
        populated_manager,
    ) -> None:
        populated_manager.remove_one_value(
            ["items", 1]
        )

        assert populated_manager.collection["items"] == [
            10,
            {
                "value": 30,
            },
        ]

    def test_remove_one_value_should_raise_for_empty_keys(
        self,
        manager,
    ) -> None:
        with pytest.raises(ValueError):
            manager.remove_one_value([])

    def test_remove_one_value_should_raise_for_missing_key(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(KeyError):
            populated_manager.remove_one_value(
                ["root", "missing"]
            )

    def test_remove_one_value_should_raise_for_missing_parent(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(KeyError):
            populated_manager.remove_one_value(
                ["missing", "value"]
            )

    def test_remove_one_value_should_raise_for_invalid_list_key_type(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(TypeError):
            populated_manager.remove_one_value(
                ["items", "0"]
            )

    def test_remove_one_value_should_raise_for_invalid_list_index(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(IndexError):
            populated_manager.remove_one_value(
                ["items", 100]
            )

    def test_remove_one_value_should_raise_when_traversing_scalar(
        self,
        manager,
    ) -> None:
        manager.collection["value"] = 1

        with pytest.raises(TypeError):
            manager.remove_one_value(
                ["value", "child"]
            )

    def test_clear_all_values_should_remove_everything(
        self,
        populated_manager,
    ) -> None:
        assert populated_manager.clear_all_values()

        assert populated_manager.collection == {}

    def test_display_one_item(
        self,
        populated_manager,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        assert populated_manager.display_one_item("root")

        output = capsys.readouterr().out

        assert output == (
            f"- root: {populated_manager.collection['root']}\n"
        )

    def test_display_all_items(
        self,
        populated_manager,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        assert populated_manager.display_all_items()

        output = capsys.readouterr().out

        assert (
            output
            == json.dumps(
                populated_manager.collection,
                indent=2,
                sort_keys=False,
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )

    def test_set_one_value_should_raise_for_invalid_destination_list_key_type(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(TypeError):
            populated_manager.set_one_value(
                ["items", "invalid"],
                1,
            )


    def test_set_one_value_should_raise_for_invalid_destination_list_index(
        self,
        populated_manager,
    ) -> None:
        with pytest.raises(IndexError):
            populated_manager.set_one_value(
                ["items", 999],
                1,
            )

    def test_set_one_value_should_raise_when_traversing_scalar_inside_list(
        self,
        manager,
    ) -> None:
        manager.collection["items"] = [1]

        with pytest.raises(TypeError):
            manager.set_one_value(
                ["items", 0, "child"],
                2,
            )


    def test_set_one_value_should_raise_when_destination_is_tuple(
        self,
        manager,
    ) -> None:
        manager.collection["tuple"] = (
            1,
            2,
        )

        with pytest.raises(TypeError):
            manager.set_one_value(
                ["tuple", 0],
                3,
            )

    def test_remove_one_value_should_raise_when_destination_is_tuple(
        self,
        manager,
    ) -> None:
        manager.collection["tuple"] = (
            1,
            2,
        )

        with pytest.raises(TypeError):
            manager.remove_one_value(
                ["tuple", 0],
            )


    def test_display_one_item_should_raise_for_missing_key(
        self,
        manager,
    ) -> None:
        with pytest.raises(KeyError):
            manager.display_one_item("missing")

    def test_set_one_value_should_update_value_in_nested_list(
        self,
        manager,
    ) -> None:
        manager.collection["items"] = [
            {
                "values": [
                    1,
                    2,
                ],
            },
        ]

        assert manager.set_one_value(
            ["items", 0, "values", 1],
            100,
        )

        assert manager.collection["items"][0]["values"][1] == 100


    def test_set_one_value_should_raise_for_nested_list_invalid_key_type(
        self,
        manager,
    ) -> None:
        manager.collection["items"] = [
            {
                "values": [
                    1,
                    2,
                ],
            },
        ]

        with pytest.raises(TypeError):
            manager.set_one_value(
                ["items", 0, "values", "1"],
                100,
            )


    def test_set_one_value_should_raise_for_nested_list_index_out_of_range(
        self,
        manager,
    ) -> None:
        manager.collection["items"] = [
            {
                "values": [
                    1,
                    2,
                ],
            },
        ]

        with pytest.raises(IndexError):
            manager.set_one_value(
                ["items", 0, "values", 10],
                100,
            )

    def test_set_one_value_should_update_nested_list_destination(
        self,
        manager,
    ) -> None:
        manager.collection["root"] = {
            "values": [
                1,
                2,
            ],
        }

        assert manager.set_one_value(
            ["root", "values", 0],
            50,
        )

        assert manager.collection["root"]["values"][0] == 50


    def test_set_one_value_should_raise_for_nested_list_destination_invalid_key_type(
        self,
        manager,
    ) -> None:
        manager.collection["root"] = {
            "values": [
                1,
                2,
            ],
        }

        with pytest.raises(TypeError):
            manager.set_one_value(
                ["root", "values", "0"],
                50,
            )


    def test_set_one_value_should_raise_for_nested_list_destination_index_out_of_range(
        self,
        manager,
    ) -> None:
        manager.collection["root"] = {
            "values": [
                1,
                2,
            ],
        }

        with pytest.raises(IndexError):
            manager.set_one_value(
                ["root", "values", 10],
                50,
            )
        