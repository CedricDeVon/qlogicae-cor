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

    def test_handle_context_manager_should_return_manager_instance(
        self,
    ) -> None:
        manager = ObjectManager = MacrosManager()()

        with manager as result:
            assert result is manager

    def test_handle_context_manager_should_reset_patterns_on_exit(
        self,
    ) -> None:
        manager = MacrosManager()()

        manager.selected_identifier_pattern = r"^custom$"
        manager.selected_macros_pattern = r"\{\{(.+?)\}\}"

        with manager:
            assert manager.selected_identifier_pattern.fullmatch("custom")

        assert manager.selected_identifier_pattern.fullmatch("abc")
        assert manager.selected_macros_pattern.fullmatch("${{abc}}")

    def test_handle_singleton_should_return_same_instance(
        self,
    ) -> None:
        manager_class = MacrosManager()
        manager_class._singleton = None

        first = manager_class.get_singleton()
        second = manager_class.get_singleton()

        assert first is second

    def test_handle_singleton_should_initialize_instance_when_uninitialized(
        self,
    ) -> None:
        manager_class = MacrosManager()
        manager_class._singleton = None

        result = manager_class.get_singleton()

        assert isinstance(result, manager_class)
        assert manager_class._singleton is result

    def test_handle_manager_should_reject_undefined_attributes(
        self,
        manager,
    ) -> None:
        with pytest.raises(AttributeError):
            manager.undefined_attribute = True

    def test_handle_selected_identifier_pattern_should_update_pattern(
        self,
        manager,
    ) -> None:
        manager.selected_identifier_pattern = r"^test$"

        assert manager.selected_identifier_pattern.fullmatch("test")
        assert manager.selected_identifier_pattern.fullmatch("abc") is None

    def test_handle_selected_identifier_pattern_should_raise_for_invalid_regex(
        self,
        manager,
    ) -> None:
        with pytest.raises(Exception):
            manager.selected_identifier_pattern = "["

    def test_handle_selected_macros_pattern_should_update_pattern(
        self,
        manager,
    ) -> None:
        manager.selected_macros_pattern = r"\{\{(.+?)\}\}"

        assert manager.selected_macros_pattern.fullmatch("{{abc}}")

    def test_handle_selected_macros_pattern_should_raise_for_invalid_regex(
        self,
        manager,
    ) -> None:
        with pytest.raises(Exception):
            manager.selected_macros_pattern = "["

    def test_handle_construct_should_return_true(
        self,
        manager,
    ) -> None:
        assert manager.construct() is True

    def test_handle_setup_should_return_false_when_kwargs_are_empty(
        self,
        manager,
    ) -> None:
        assert manager.setup() is False

    def test_handle_setup_should_return_true_when_kwargs_are_provided(
        self,
        manager,
    ) -> None:
        assert manager.setup(value=1) is True

    def test_handle_shutdown_should_return_true(
        self,
        manager,
    ) -> None:
        manager.selected_identifier_pattern = r"^custom$"
        manager.selected_macros_pattern = r"\{\{(.+?)\}\}"

        assert manager.shutdown() is True

        assert manager.selected_identifier_pattern.fullmatch("abc")
        assert manager.selected_macros_pattern.fullmatch("${{abc}}")

    def test_handle_resolve_value_should_execute_callable(
        self,
        manager,
    ) -> None:
        assert manager._resolve_value(lambda: "resolved") == "resolved"

    def test_handle_resolve_value_should_preserve_non_callable_value(
        self,
        manager,
    ) -> None:
        value = {"a": 1}

        assert manager._resolve_value(value) is value

    def test_resolve_many_should_handle_empty_mapping(
        self,
        manager,
    ) -> None:
        assert manager.resolve_many({}) == {}

    def test_resolve_many_should_resolve_callable_values(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": lambda: "resolved",
                "b": "${{a}}",
            }
        )

        assert result == {
            "a": "resolved",
            "b": "resolved",
        }

    def test_resolve_many_should_execute_callable_only_once(
        self,
        manager,
    ) -> None:
        calls = []

        def resolve():
            calls.append(True)
            return "resolved"

        result = manager.resolve_many(
            {
                "a": resolve,
                "b": "${{a}}",
                "c": "${{a}}",
            }
        )

        assert result == {
            "a": "resolved",
            "b": "resolved",
            "c": "resolved",
        }
        assert len(calls) == 1

    def test_resolve_many_should_resolve_multiple_independent_callable_values(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": lambda: 1,
                "b": lambda: 2,
                "c": "${{a}}-${{b}}",
            }
        )

        assert result == {
            "a": 1,
            "b": 2,
            "c": "1-2",
        }

    def test_resolve_many_should_resolve_duplicate_dependencies(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": "value",
                "b": "${{a}}-${{a}}-${{a}}",
                "c": "${{b}}-${{a}}",
            }
        )

        assert result == {
            "a": "value",
            "b": "value-value-value",
            "c": "value-value-value-value",
        }

    def test_resolve_many_should_raise_for_indirect_circular_reference(
        self,
        manager,
    ) -> None:
        with pytest.raises(ValueError):
            manager.resolve_many(
                {
                    "a": "${{b}}",
                    "b": "${{c}}",
                    "c": "${{a}}",
                }
            )

    def test_resolve_many_should_resolve_callable_returning_none(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": lambda: None,
                "b": "${{a}}",
            }
        )

        assert result == {
            "a": None,
            "b": "None",
        }

    def test_resolve_one_should_resolve_callable_value(
        self,
        manager,
    ) -> None:
        cache = {}

        result = manager.resolve_one(
            "a",
            {
                "a": lambda: "resolved",
            },
            cache,
            set(),
        )

        assert result == "resolved"
        assert cache == {
            "a": "resolved",
        }

    def test_resolve_one_should_execute_callable_only_once(
        self,
        manager,
    ) -> None:
        calls = []

        def resolve():
            calls.append(True)
            return "resolved"

        cache = {}

        first = manager.resolve_one(
            "a",
            {
                "a": resolve,
            },
            cache,
            set(),
        )

        second = manager.resolve_one(
            "a",
            {
                "a": resolve,
            },
            cache,
            set(),
        )

        assert first == second == "resolved"
        assert len(calls) == 1

    def test_resolve_one_should_resolve_callable_dependency(
        self,
        manager,
    ) -> None:
        result = manager.resolve_one(
            "b",
            {
                "a": lambda: "resolved",
                "b": "${{a}}",
            },
            {},
            set(),
        )

        assert result == "resolved"

    def test_resolve_one_should_resolve_multiple_dependencies(
        self,
        manager,
    ) -> None:
        result = manager.resolve_one(
            "c",
            {
                "a": "1",
                "b": "2",
                "c": "${{a}}-${{b}}",
            },
            {},
            set(),
        )

        assert result == "1-2"

    def test_resolve_one_should_resolve_duplicate_dependencies(
        self,
        manager,
    ) -> None:
        result = manager.resolve_one(
            "b",
            {
                "a": "value",
                "b": "${{a}}-${{a}}-${{a}}",
            },
            {},
            set(),
        )

        assert result == "value-value-value"

    def test_resolve_one_should_raise_for_indirect_circular_dependency(
        self,
        manager,
    ) -> None:
        with pytest.raises(ValueError):
            manager.resolve_one(
                "a",
                {
                    "a": "${{b}}",
                    "b": "${{c}}",
                    "c": "${{a}}",
                },
                {},
                set(),
            )

    def test_resolve_one_should_resolve_long_dependency_chain(
        self,
        manager,
    ) -> None:
        result = manager.resolve_one(
            "e",
            {
                "a": "1",
                "b": "${{a}}",
                "c": "${{b}}",
                "d": "${{c}}",
                "e": "${{d}}",
            },
            {},
            set(),
        )

        assert result == "1"

    def test_resolve_one_should_preserve_existing_cache_entries(
        self,
        manager,
    ) -> None:
        cache = {
            "a": "cached",
        }

        result = manager.resolve_one(
            "a",
            {
                "a": "original",
            },
            cache,
            set(),
        )

        assert result == "cached"
        assert cache == {
            "a": "cached",
        }

    def test_parse_filesystem_should_return_true(
        self,
        manager,
        tmp_path,
    ) -> None:
        assert manager.parse_filesystem(
            tmp_path,
            {},
        ) is True

    def test_parse_filesystem_should_parse_file_contents(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "config.txt"
        file_path.write_text(
            "value=${{value}}",
            encoding="utf-8",
        )

        result = manager.parse_filesystem(
            tmp_path,
            {
                "value": "resolved",
            },
        )

        assert result is True
        assert file_path.read_text(encoding="utf-8") == "value=resolved"

    def test_parse_filesystem_should_preserve_unchanged_file_contents(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "config.txt"
        file_path.write_text(
            "unchanged",
            encoding="utf-8",
        )

        manager.parse_filesystem(
            tmp_path,
            {},
        )

        assert file_path.read_text(encoding="utf-8") == "unchanged"

    def test_parse_filesystem_should_parse_file_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "config-${{name}}.txt"
        file_path.write_text(
            "value",
            encoding="utf-8",
        )

        manager.parse_filesystem(
            tmp_path,
            {
                "name": "resolved",
            },
        )

        assert (tmp_path / "config-resolved.txt").exists()

    def test_parse_filesystem_should_parse_directory_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        directory = tmp_path / "directory-${{name}}"
        directory.mkdir()

        manager.parse_filesystem(
            tmp_path,
            {
                "name": "resolved",
            },
        )

        assert (tmp_path / "directory-resolved").is_dir()

    def test_parse_filesystem_should_parse_nested_directory_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        directory = tmp_path / "directory-${{name}}"
        nested_directory = directory / "nested-${{name}}"
        nested_directory.mkdir(parents=True)

        manager.parse_filesystem(
            tmp_path,
            {
                "name": "resolved",
            },
        )

        assert (tmp_path / "directory-resolved").is_dir()
        assert (tmp_path / "directory-resolved" / "nested-resolved").is_dir()

    def test_parse_filesystem_should_parse_nested_file_contents(
        self,
        manager,
        tmp_path,
    ) -> None:
        directory = tmp_path / "directory"
        directory.mkdir()

        file_path = directory / "config.txt"
        file_path.write_text(
            "${{value}}",
            encoding="utf-8",
        )

        manager.parse_filesystem(
            tmp_path,
            {
                "value": "resolved",
            },
        )

        assert file_path.read_text(encoding="utf-8") == "resolved"

    def test_parse_filesystem_should_parse_file_contents_and_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "config-${{name}}.txt"
        file_path.write_text(
            "${{value}}",
            encoding="utf-8",
        )

        manager.parse_filesystem(
            tmp_path,
            {
                "name": "resolved",
                "value": "content",
            },
        )

        renamed_path = tmp_path / "config-resolved.txt"

        assert renamed_path.exists()
        assert renamed_path.read_text(encoding="utf-8") == "content"

    def test_parse_filesystem_should_parse_directory_and_file_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        directory = tmp_path / "directory-${{name}}"
        directory.mkdir()

        file_path = directory / "file-${{name}}.txt"
        file_path.write_text("content", encoding="utf-8")

        manager.parse_filesystem(
            tmp_path,
            {
                "name": "resolved",
            },
        )

        renamed_directory = tmp_path / "directory-resolved"
        renamed_file = renamed_directory / "file-resolved.txt"

        assert renamed_directory.is_dir()
        assert renamed_file.is_file()

    def test_parse_filesystem_should_ignore_unicode_decode_errors(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "binary-${{name}}.bin"
        file_path.write_bytes(b"\x80\x81\xfe\xff")

        result = manager.parse_filesystem(
            tmp_path,
            {
                "name": "resolved",
            },
        )

        renamed_path = tmp_path / "binary-resolved.bin"

        assert result is True
        assert renamed_path.exists()
        assert renamed_path.read_bytes() == b"\x80\x81\xfe\xff"

    def test_parse_filesystem_should_ignore_binary_files_without_macros(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "binary.bin"
        file_path.write_bytes(b"\x80\x81\xfe\xff")

        manager.parse_filesystem(
            tmp_path,
            {},
        )

        assert file_path.exists()
        assert file_path.read_bytes() == b"\x80\x81\xfe\xff"

    def test_parse_filesystem_should_handle_multiple_files(
        self,
        manager,
        tmp_path,
    ) -> None:
        first_file = tmp_path / "first.txt"
        second_file = tmp_path / "second.txt"

        first_file.write_text("${{value}}", encoding="utf-8")
        second_file.write_text("${{value}}", encoding="utf-8")

        manager.parse_filesystem(
            tmp_path,
            {
                "value": "resolved",
            },
        )

        assert first_file.read_text(encoding="utf-8") == "resolved"
        assert second_file.read_text(encoding="utf-8") == "resolved"

    def test_parse_filesystem_should_raise_when_parsed_file_contents_are_not_strings(
        self,
        manager,
        tmp_path,
        monkeypatch,
    ) -> None:
        file_path = tmp_path / "config.txt"
        file_path.write_text("content", encoding="utf-8")

        monkeypatch.setattr(
            type(manager),
            "parse_one",
            lambda self, value, resolved: None,
        )

        with pytest.raises(TypeError, match="parsed file data must be a string"):
            manager.parse_filesystem(tmp_path, {})

    def test_parse_filesystem_should_raise_when_parsed_file_names_are_not_strings(
        self,
        manager,
        tmp_path,
        monkeypatch,
    ) -> None:
        file_path = tmp_path / "binary.bin"
        file_path.write_bytes(b"\x80\x81\xfe\xff")

        monkeypatch.setattr(
            type(manager),
            "parse_one",
            lambda self, value, resolved: None,
        )

        with pytest.raises(TypeError, match="parsed file name must be a string"):
            manager.parse_filesystem(tmp_path, {})

    def test_parse_filesystem_should_raise_when_parsed_directory_names_are_not_strings(
        self,
        manager,
        tmp_path,
        monkeypatch,
    ) -> None:
        (tmp_path / "directory").mkdir()

        monkeypatch.setattr(
            type(manager),
            "parse_one",
            lambda self, value, resolved: None,
        )

        with pytest.raises(
            TypeError,
            match="parsed directory name must be a string",
        ):
            manager.parse_filesystem(tmp_path, {})

    def test_setup_should_return_false_without_kwargs(
        self,
        manager,
    ) -> None:
        assert manager.setup() is False

    def test_setup_should_return_true_with_kwargs(
        self,
        manager,
    ) -> None:
        assert manager.setup(identifier_pattern="^[a-z]+$") is True

    def test_context_manager_should_reset_patterns_on_exit(
        self,
    ) -> None:
        manager = MacrosManager()()

        manager.selected_identifier_pattern = r"^[a-z]+$"
        manager.selected_macros_pattern = r"\$\{\{([a-z]+)\}\}"

        with manager:
            assert manager.selected_identifier_pattern.fullmatch("abc")
            assert manager.selected_macros_pattern.fullmatch("${{abc}}")

        assert manager.selected_identifier_pattern.fullmatch("ABC")
        assert manager.selected_macros_pattern.fullmatch("${{abc}}")

    def test_context_manager_should_reset_patterns_after_exception(
        self,
    ) -> None:
        manager = MacrosManager()()

        manager.selected_identifier_pattern = r"^[a-z]+$"

        with pytest.raises(RuntimeError):
            with manager:
                raise RuntimeError("failure")

        assert manager.selected_identifier_pattern.fullmatch("ABC")

    def test_resolve_value_should_return_non_callable_value(
        self,
        manager,
    ) -> None:
        value = object()

        assert manager._resolve_value(value) is value

    def test_resolve_value_should_execute_callable(
        self,
        manager,
    ) -> None:
        assert manager._resolve_value(lambda: "resolved") == "resolved"

    def test_resolve_many_should_return_empty_mapping(
        self,
        manager,
    ) -> None:
        assert manager.resolve_many({}) == {}

    def test_resolve_many_should_resolve_callable_value(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": lambda: "resolved",
            }
        )

        assert result == {
            "a": "resolved",
        }

    def test_resolve_many_should_resolve_callable_dependency(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": lambda: "resolved",
                "b": "value=${{a}}",
            }
        )

        assert result == {
            "a": "resolved",
            "b": "value=resolved",
        }

    def test_resolve_many_should_execute_callable_once(
        self,
        manager,
    ) -> None:
        calls = []

        def resolve():
            calls.append("called")
            return "resolved"

        result = manager.resolve_many(
            {
                "a": resolve,
                "b": "${{a}}-${{a}}",
            }
        )

        assert result == {
            "a": "resolved",
            "b": "resolved-resolved",
        }
        assert calls == ["called"]

    def test_resolve_many_should_resolve_repeated_dependencies(
        self,
        manager,
    ) -> None:
        result = manager.resolve_many(
            {
                "a": "first",
                "b": "${{a}}",
                "c": "${{a}}",
                "d": "${{b}}-${{c}}-${{a}}",
            }
        )

        assert result == {
            "a": "first",
            "b": "first",
            "c": "first",
            "d": "first-first-first",
        }

    def test_resolve_one_should_execute_callable_once(
        self,
        manager,
    ) -> None:
        calls = []

        def resolve():
            calls.append("called")
            return "resolved"

        assert manager.resolve_one(
            "b",
            {
                "a": resolve,
                "b": "${{a}}-${{a}}",
            },
            {},
            set(),
        ) == "resolved-resolved"

        assert calls == ["called"]

    def test_resolve_one_should_reuse_cached_dependency(
        self,
        manager,
    ) -> None:
        cache = {
            "a": "cached",
        }

        assert manager.resolve_one(
            "b",
            {
                "a": "uncached",
                "b": "${{a}}-${{a}}",
            },
            cache,
            set(),
        ) == "cached-cached"

        assert cache == {
            "a": "cached",
            "b": "cached-cached",
        }

    def test_resolve_one_should_not_modify_supplied_stack(
        self,
        manager,
    ) -> None:
        stack = set()

        manager.resolve_one(
            "a",
            {
                "a": "resolved",
            },
            {},
            stack,
        )

        assert stack == set()

    def test_parse_one_should_resolve_callable_macro(
        self,
        manager,
    ) -> None:
        assert manager.parse_one(
            "value=${{a}}",
            {
                "a": lambda: "resolved",
            },
        ) == "value=resolved"

    def test_parse_one_should_resolve_callable_macro_for_each_occurrence(
        self,
        manager,
    ) -> None:
        calls = []

        def resolve():
            calls.append("called")
            return len(calls)

        assert manager.parse_one(
            "${{a}}-${{a}}",
            {
                "a": resolve,
            },
        ) == "1-2"

        assert calls == ["called", "called"]

    def test_parse_filesystem_should_preserve_unchanged_file_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "example.txt"
        file_path.write_text("content", encoding="utf-8")

        assert manager.parse_filesystem(tmp_path, {}) is True

        assert file_path.is_file()

    def test_parse_filesystem_should_preserve_unchanged_directory_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        directory_path = tmp_path / "directory"
        directory_path.mkdir()

        assert manager.parse_filesystem(tmp_path, {}) is True

        assert directory_path.is_dir()

    def test_parse_filesystem_should_parse_file_contents_and_file_names(
        self,
        manager,
        tmp_path,
    ) -> None:
        file_path = tmp_path / "file-${{name}}.txt"
        file_path.write_text("${{name}}", encoding="utf-8")

        assert manager.parse_filesystem(
            tmp_path,
            {
                "name": "resolved",
            },
        ) is True

        parsed_file_path = tmp_path / "file-resolved.txt"

        assert parsed_file_path.is_file()
        assert parsed_file_path.read_text(encoding="utf-8") == "resolved"

    def test_parse_filesystem_should_return_true_for_empty_directory(
        self,
        manager,
        tmp_path,
    ) -> None:
        assert manager.parse_filesystem(tmp_path, {}) is True

    def test_parse_filesystem_should_raise_for_non_string_file_contents(
        self,
        manager,
        tmp_path,
        monkeypatch,
    ) -> None:
        file_path = tmp_path / "example.txt"
        file_path.write_text("content", encoding="utf-8")

        monkeypatch.setattr(
            type(manager),
            "parse_one",
            lambda self, value, resolved: None,
        )

        with pytest.raises(TypeError, match="parsed file data must be a string"):
            manager.parse_filesystem(tmp_path, {})

    def test_parse_filesystem_should_raise_for_non_string_file_names(
        self,
        manager,
        tmp_path,
        monkeypatch,
    ) -> None:
        file_path = tmp_path / "example.txt"
        file_path.write_text("content", encoding="utf-8")

        calls = []

        def parse_one(self, value, resolved):
            calls.append(value)

            if value == file_path.name:
                return None

            return value

        monkeypatch.setattr(type(manager), "parse_one", parse_one)

        with pytest.raises(TypeError, match="parsed file name must be a string"):
            manager.parse_filesystem(tmp_path, {})

    def test_parse_filesystem_should_raise_for_non_string_directory_names(
        self,
        manager,
        tmp_path,
        monkeypatch,
    ) -> None:
        directory_path = tmp_path / "example"
        directory_path.mkdir()

        monkeypatch.setattr(
            type(manager),
            "parse_one",
            lambda self, value, resolved: None,
        )

        with pytest.raises(TypeError, match="parsed directory name must be a string"):
            manager.parse_filesystem(tmp_path, {})

