import re

import pytest

from qlogicae_cor.v3.library.macros_manager import MacrosManager


class TestMacrosManager:
    @pytest.fixture
    def manager(self):
        return MacrosManager()()

    def test_identifier_pattern_should_match_valid_identifier(
        self,
        manager,
    ) -> None:
        assert manager.selected_identifier_pattern.fullmatch("abc")
        assert manager.selected_identifier_pattern.fullmatch("abc.def")
        assert manager.selected_identifier_pattern.fullmatch("abc_def")
        assert manager.selected_identifier_pattern.fullmatch("abc-def")
        assert manager.selected_identifier_pattern.fullmatch("A1.b_c-d")

    def test_identifier_pattern_should_reject_invalid_identifier(
        self,
        manager,
    ) -> None:
        assert manager.selected_identifier_pattern.fullmatch("abc def") is None
        assert manager.selected_identifier_pattern.fullmatch("abc$") is None
        assert manager.selected_identifier_pattern.fullmatch("") is None

    def test_macros_pattern_should_find_macros(
        self,
        manager,
    ) -> None:
        matches = list(manager.selected_macros_pattern.finditer("x=${{a}} y=${{ b.c }}"))

        assert len(matches) == 2
        assert matches[0].group(1) == "a"
        assert matches[1].group(1) == "b.c"

    def test_resolve_many_should_raise_for_non_mapping(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.resolve_many([])

    def test_resolve_many_should_raise_for_non_string_key(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.resolve_many({1: "value"})

    def test_resolve_many_should_raise_for_invalid_identifier(
        self,
        manager,
    ) -> None:
        with pytest.raises(ValueError):
            manager.resolve_many({"invalid key": "value"})

    def test_resolve_many_should_resolve_independent_macros(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": "1",
                "b": "2",
            }
        )

        assert result == {
            "a": "1",
            "b": "2",
        }

    def test_resolve_many_should_resolve_nested_macros(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": "1",
                "b": "${{a}}",
                "c": "${{b}}",
                "d": "value=${{c}}",
            }
        )

        assert result == {
            "a": "1",
            "b": "1",
            "c": "1",
            "d": "value=1",
        }

    def test_resolve_many_should_preserve_non_string_values(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": 1,
                "b": True,
                "c": None,
                "d": [1],
                "e": {"x": 1},
            }
        )

        assert result == {
            "a": 1,
            "b": True,
            "c": None,
            "d": [1],
            "e": {"x": 1},
        }

    def test_resolve_many_should_resolve_multiple_macros(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": "1",
                "b": "2",
                "c": "${{a}}-${{b}}",
            }
        )

        assert result["c"] == "1-2"

    def test_resolve_many_should_raise_for_unknown_macro(
        self,
        manager,
    ) -> None:
        with pytest.raises(Exception):
            manager.resolve_many(
                {
                    "a": "${{missing}}",
                }
            )

    def test_resolve_many_should_raise_for_circular_reference(
        self,
        manager,
    ) -> None:
        with pytest.raises(Exception):
            manager.resolve_many(
                {
                    "a": "${{b}}",
                    "b": "${{a}}",
                }
            )

    def test_resolve_one_should_raise_for_invalid_key_type(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.resolve_one(
                1,
                {},
                {},
                set(),
            )

    def test_resolve_one_should_raise_for_invalid_values_type(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.resolve_one(
                "a",
                [],
                {},
                set(),
            )

    def test_resolve_one_should_raise_for_invalid_cache_type(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.resolve_one(
                "a",
                {},
                [],
                set(),
            )

    def test_resolve_one_should_raise_for_invalid_stack_type(
        self,
        manager,
    ) -> None:
        with pytest.raises(TypeError):
            manager.resolve_one(
                "a",
                {},
                {},
                [],
            )

    def test_resolve_one_should_raise_for_unknown_root_macro(
        self,
        manager,
    ) -> None:
        with pytest.raises(KeyError):
            manager.resolve_one(
                "missing",
                {},
                {},
                set(),
            )

    def test_resolve_one_should_return_cached_value(
        self,
        manager,
    ) -> None:
        cache = {
            "a": "cached",
        }

        result = manager.resolve_one(
            "a",
            {
                "a": "ignored",
            },
            cache,
            set(),
        )

        assert result == "cached"

    def test_resolve_one_should_resolve_single_macro(
        self,
        manager,
    ) -> None:
        values = {
            "a": "1",
        }

        cache = {}

        assert manager.resolve_one(
            "a",
            values,
            cache,
            set(),
        ) == "1"

        assert cache == {
            "a": "1",
        }

    def test_resolve_one_should_resolve_nested_macros(
        self,
        manager,
    ) -> None:
        values = {
            "a": "1",
            "b": "${{a}}",
            "c": "v=${{b}}",
        }

        cache = {}

        assert (
            manager.resolve_one(
                "c",
                values,
                cache,
                set(),
            )
            == "v=1"
        )

        assert cache == {
            "a": "1",
            "b": "1",
            "c": "v=1",
        }

    def test_resolve_one_should_preserve_non_string_value(
        self,
        manager,
    ) -> None:
        cache = {}

        assert (
            manager.resolve_one(
                "a",
                {
                    "a": 123,
                },
                cache,
                set(),
            )
            == 123
        )

        assert cache == {
            "a": 123,
        }

    def test_resolve_one_should_raise_for_unknown_dependency(
        self,
        manager,
    ) -> None:
        with pytest.raises(KeyError):
            manager.resolve_one(
                "a",
                {
                    "a": "${{missing}}",
                },
                {},
                set(),
            )

    def test_resolve_one_should_raise_for_circular_dependency(
        self,
        manager,
    ) -> None:
        with pytest.raises(ValueError):
            manager.resolve_one(
                "a",
                {
                    "a": "${{b}}",
                    "b": "${{a}}",
                },
                {},
                set(),
            )

    def test_parse_many_should_delegate_to_parse_one(
        self,
        manager,
    ) -> None:
        assert manager.parse_many(
            "${{a}}",
            {
                "a": "1",
            },
        ) == "1"

    def test_parse_one_should_parse_string(
        self,
        manager,
    ) -> None:
        assert (
            manager.parse_one(
                "x=${{a}}",
                {
                    "a": "1",
                },
            )
            == "x=1"
        )

    def test_parse_one_should_leave_unknown_macro(
        self,
        manager,
    ) -> None:
        assert (
            manager.parse_one(
                "x=${{missing}}",
                {},
            )
            == "x=${{missing}}"
        )

    def test_parse_one_should_parse_dictionary(
        self,
        manager,
    ) -> None:
        value = {
            "a": "${{x}}",
            "b": {
                "c": "${{y}}",
            },
        }

        assert manager.parse_one(
            value,
            {
                "x": "1",
                "y": "2",
            },
        ) == {
            "a": "1",
            "b": {
                "c": "2",
            },
        }

    def test_parse_one_should_parse_list(
        self,
        manager,
    ) -> None:
        assert manager.parse_one(
            [
                "${{a}}",
                "${{b}}",
            ],
            {
                "a": "1",
                "b": "2",
            },
        ) == [
            "1",
            "2",
        ]

    def test_parse_one_should_parse_tuple(
        self,
        manager,
    ) -> None:
        assert manager.parse_one(
            (
                "${{a}}",
                "${{b}}",
            ),
            {
                "a": "1",
                "b": "2",
            },
        ) == (
            "1",
            "2",
        )

    def test_parse_one_should_parse_set(
        self,
        manager,
    ) -> None:
        assert manager.parse_one(
            {
                "${{a}}",
                "${{b}}",
            },
            {
                "a": "1",
                "b": "2",
            },
        ) == {
            "1",
            "2",
        }

    @pytest.mark.parametrize(
        "value",
        [
            1,
            1.5,
            True,
            None,
            re.compile("x"),
            object(),
        ],
    )
    def test_parse_one_should_return_non_container_values_unchanged(
        self,
        manager,
        value,
    ) -> None:
        assert manager.parse_one(value, {}) is value

    def test_resolve_many_should_reuse_cached_root(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "b": "${{a}}",
                "a": "1",
            }
        )

        assert result == {
            "a": "1",
            "b": "1",
        }


    def test_resolve_many_should_reuse_cached_dependency(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": "1",
                "b": "${{a}}",
                "c": "${{a}}",
                "d": "${{a}}-${{b}}-${{c}}",
            }
        )

        assert result == {
            "a": "1",
            "b": "1",
            "c": "1",
            "d": "1-1-1",
        }


    def test_resolve_many_should_resolve_long_dependency_chain(
        self,
        manager,
    ) -> None:
        values = {
            "a": "1",
            "b": "${{a}}",
            "c": "${{b}}",
            "d": "${{c}}",
            "e": "${{d}}",
            "f": "value=${{e}}",
        }

        assert manager.resolve_many(values) == {
            "a": "1",
            "b": "1",
            "c": "1",
            "d": "1",
            "e": "1",
            "f": "value=1",
        }


    def test_resolve_many_should_replace_multiple_occurrences_of_same_macro(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": "1",
                "b": "${{a}}-${{a}}-${{a}}",
            }
        )

        assert result["b"] == "1-1-1"


    def test_resolve_one_should_skip_cached_frame(
        self,
        manager,
    ) -> None:
        values = {
            "a": "1",
            "b": "${{a}}",
            "c": "${{a}}",
            "d": "${{b}}-${{c}}",
        }

        cache = {}

        assert (
            manager.resolve_one(
                "d",
                values,
                cache,
                set(),
            )
            == "1-1"
        )

        assert cache == {
            "a": "1",
            "b": "1",
            "c": "1",
            "d": "1-1",
        }


    def test_resolve_one_should_replace_multiple_macros(
        self,
        manager,
    ) -> None:
        values = {
            "a": "1",
            "b": "2",
            "c": "${{a}}:${{b}}:${{a}}",
        }

        assert (
            manager.resolve_one(
                "c",
                values,
                {},
                set(),
            )
            == "1:2:1"
        )


    def test_resolve_one_should_resolve_long_dependency_chain(
        self,
        manager,
    ) -> None:
        values = {
            "a": "1",
            "b": "${{a}}",
            "c": "${{b}}",
            "d": "${{c}}",
            "e": "${{d}}",
        }

        assert (
            manager.resolve_one(
                "e",
                values,
                {},
                set(),
            )
            == "1"
        )


    def test_parse_many_should_parse_dictionary(
        self,
        manager,
    ) -> None:
        value = {
            "a": "${{x}}",
        }

        assert manager.parse_many(
            value,
            {
                "x": "1",
            },
        ) == {
            "a": "1",
        }


    def test_parse_many_should_parse_list(
        self,
        manager,
    ) -> None:
        assert manager.parse_many(
            [
                "${{a}}",
            ],
            {
                "a": "1",
            },
        ) == [
            "1",
        ]


    def test_parse_many_should_parse_tuple(
        self,
        manager,
    ) -> None:
        assert manager.parse_many(
            (
                "${{a}}",
            ),
            {
                "a": "1",
            },
        ) == (
            "1",
        )


    def test_parse_many_should_parse_set(
        self,
        manager,
    ) -> None:
        assert manager.parse_many(
            {
                "${{a}}",
            },
            {
                "a": "1",
            },
        ) == {
            "1",
        }


    def test_parse_one_should_return_empty_string(
        self,
        manager,
    ) -> None:
        assert manager.parse_one("", {}) == ""


    def test_parse_one_should_return_string_without_macros(
        self,
        manager,
    ) -> None:
        assert manager.parse_one("hello world", {}) == "hello world"


    @pytest.mark.parametrize(
        "value",
        [
            {},
            [],
            (),
            set(),
        ],
    )
    def test_parse_one_should_handle_empty_containers(
        self,
        manager,
        value,
    ) -> None:
        assert manager.parse_one(value, {}) == value


    def test_parse_one_should_parse_deeply_nested_structure(
        self,
        manager,
    ) -> None:
        value = {
            "a": [
                {
                    "b": (
                        "${{x}}",
                        {
                            "${{y}}",
                        },
                    ),
                },
            ],
        }

        assert manager.parse_one(
            value,
            {
                "x": "1",
                "y": "2",
            },
        ) == {
            "a": [
                {
                    "b": (
                        "1",
                        {
                            "2",
                        },
                    ),
                },
            ],
        }


    def test_parse_one_should_preserve_nested_non_string_values(
        self,
        manager,
    ) -> None:
        sentinel = object()

        value = {
            "a": [
                1,
                True,
                None,
                sentinel,
                {
                    "b": 2.5,
                },
            ],
        }

        result = manager.parse_one(value, {})

        assert result["a"][0] == 1
        assert result["a"][1] is True
        assert result["a"][2] is None
        assert result["a"][3] is sentinel
        assert result["a"][4]["b"] == 2.5
