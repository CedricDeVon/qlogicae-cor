__all__ = (
    "MacrosManager",
)

_re = None
_Path = None
_Mapping = None
_TextEncodingManager = None
_PythonRuntimeUtilityManager = None
_MacrosManager = None


def _allocate_module():
    global _allocate_module
    global _re
    global _Path
    global _Mapping
    global _TextEncodingManager
    global _PythonRuntimeUtilityManager
    global _MacrosManager

    import re
    from collections.abc import Mapping
    from pathlib import Path

    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .text_encoding_manager import TextEncodingManager

    _re = re
    _Path = Path
    _Mapping = Mapping
    _TextEncodingManager = TextEncodingManager().get_singleton
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()

    class __MacrosManager:
        __slots__ = (
            "_selected_identifier_pattern",
            "_selected_macros_pattern",
        )

        _singleton = None

        def __init__(self):
            if (
                _PythonRuntimeUtilityManager
                .is_allocated_during_object_construction
            ):
                _TextEncodingManager()

            self._selected_identifier_pattern = (
                _re.compile(r"^[A-Za-z0-9._-]+$")
            )
            self._selected_macros_pattern = (
                _re.compile(r"\$\{\{\s*([A-Za-z0-9._-]+)\s*\}\}")
            )

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def selected_identifier_pattern(self):
            return self._selected_identifier_pattern

        @selected_identifier_pattern.setter
        def selected_identifier_pattern(self, value):
            self._selected_identifier_pattern = _re.compile(value)

        @property
        def selected_macros_pattern(self):
            return self._selected_macros_pattern

        @selected_macros_pattern.setter
        def selected_macros_pattern(self, value):
            self._selected_macros_pattern = _re.compile(value)

        def _resolve_value(self, value):
            if callable(value):
                return value()

            return value

        def resolve_many(self, values):
            if not isinstance(values, _Mapping):
                raise TypeError("'values' must be a mapping")

            for key in values:
                if not isinstance(key, str):
                    raise TypeError("macro names must be strings")

                if not self._selected_identifier_pattern.fullmatch(key):
                    raise ValueError(
                        f"invalid macro name: '{key}'",
                    )

            cache = {}

            for root in values:
                if root in cache:
                    continue

                stack = [root]
                visiting = set()

                while stack:
                    key = stack[-1]

                    if key in cache:
                        stack.pop()
                        visiting.discard(key)
                        continue

                    if key not in values:
                        raise ValueError(
                            f"key path '{key}' is an unknown macro",
                        )

                    value = values[key]

                    if not isinstance(value, str):
                        cache[key] = self._resolve_value(value)
                        stack.pop()
                        visiting.discard(key)
                        continue

                    visiting.add(key)

                    dependencies = []

                    for match in self._selected_macros_pattern.finditer(
                        value,
                    ):
                        dependency = match.group(1)

                        if dependency in cache:
                            continue

                        if dependency not in values:
                            raise ValueError(
                                f"key path '{key}' references unknown macro "
                                f"'{dependency}'",
                            )

                        if dependency in visiting:
                            raise ValueError(
                                f"circular macro reference: "
                                f"'{key}' -> '{dependency}'",
                            )

                        if dependency not in dependencies:
                            dependencies.append(dependency)

                    if dependencies:
                        stack.extend(reversed(dependencies))
                        continue

                    def replace(match):
                        dependency = match.group(1)
                        return str(cache[dependency])

                    cache[key] = self._selected_macros_pattern.sub(
                        replace,
                        value,
                    )

                    stack.pop()
                    visiting.remove(key)

            return cache

        def resolve_one(
            self,
            key,
            values,
            cache,
            stack,
        ):
            if not isinstance(key, str):
                raise TypeError("'key' must be a string")

            if not isinstance(values, _Mapping):
                raise TypeError("'values' must be a mapping")

            if not isinstance(cache, dict):
                raise TypeError("'cache' must be a dictionary")

            if not isinstance(stack, set):
                raise TypeError("'stack' must be a set")

            if key not in values:
                raise KeyError(f"unknown macro '{key}'")

            if key in cache:
                return cache[key]

            frames = [
                (key, False),
            ]

            while frames:
                current_key, expanded = frames.pop()

                if current_key in cache:
                    continue

                if not expanded:
                    if current_key in stack:
                        raise ValueError(
                            f"key path '{current_key}' is a circular reference",
                        )

                    if current_key not in values:
                        raise ValueError(
                            f"key path '{current_key}' is an unknown macro",
                        )

                    value = values[current_key]

                    if not isinstance(value, str):
                        cache[current_key] = self._resolve_value(value)
                        continue

                    stack.add(current_key)

                    frames.append(
                        (current_key, True),
                    )

                    dependencies = []

                    for match in self._selected_macros_pattern.finditer(
                        value,
                    ):
                        dependency = match.group(1)

                        if dependency not in values:
                            raise KeyError(
                                f"macro '{current_key}' references unknown "
                                f"macro '{dependency}'",
                            )

                        if dependency in stack:
                            raise ValueError(
                                f"circular macro reference: "
                                f"'{current_key}' -> '{dependency}'",
                            )

                        if dependency not in cache:
                            if dependency not in dependencies:
                                dependencies.append(dependency)

                    frames.extend(
                        (dependency, False)
                        for dependency in reversed(dependencies)
                    )

                else:
                    value = values[current_key]

                    if not isinstance(value, str):
                        cache[current_key] = self._resolve_value(value)
                    else:
                        cache[current_key] = (
                            self._selected_macros_pattern.sub(
                                lambda match: str(cache[match.group(1)]),
                                value,
                            )
                        )

                    stack.remove(current_key)

            return cache[key]

        def parse_many(self, values, resolved):
            return self.parse_one(
                values,
                resolved,
            )

        def parse_one(self, value, resolved):
            if isinstance(value, str):

                def replace(match):
                    key = match.group(1)

                    if key not in resolved:
                        return str(match.group(0))

                    return str(
                        self._resolve_value(
                            resolved[key]
                        )
                    )

                return self._selected_macros_pattern.sub(
                    replace,
                    value,
                )

            if isinstance(value, dict):
                return {
                    key: self.parse_one(
                        child,
                        resolved,
                    )
                    for key, child in value.items()
                }

            if isinstance(value, list):
                return [
                    self.parse_one(
                        child,
                        resolved,
                    )
                    for child in value
                ]

            if isinstance(value, tuple):
                return tuple(
                    self.parse_one(
                        child,
                        resolved,
                    )
                    for child in value
                )

            if isinstance(value, set):
                return {
                    self.parse_one(
                        child,
                        resolved,
                    )
                    for child in value
                }

            return value

        def parse_filesystem(
            self,
            filesystem_path,
            workspace_macros,
        ):
            encoding = _TextEncodingManager().selected_encoding
            root = _Path(filesystem_path)

            for current_root, directories, files in root.walk(
                top_down=False,
            ):
                current_root = _Path(current_root)

                for file_name in files:
                    current_path = current_root / file_name

                    try:
                        file_data = current_path.read_text(
                            encoding=encoding,
                        )
                    except UnicodeDecodeError:
                        pass
                    else:
                        parsed_file_data = self.parse_one(
                            file_data,
                            workspace_macros,
                        )

                        if not isinstance(parsed_file_data, str):
                            raise TypeError(
                                "parsed file data must be a string",
                            )

                        if parsed_file_data != file_data:
                            current_path.write_text(
                                parsed_file_data,
                                encoding=encoding,
                            )

                    parsed_name = self.parse_one(
                        current_path.name,
                        workspace_macros,
                    )

                    if not isinstance(parsed_name, str):
                        raise TypeError(
                            "parsed file name must be a string",
                        )

                    if parsed_name != current_path.name:
                        current_path = current_path.rename(
                            current_path.with_name(parsed_name),
                        )

                for directory_name in directories:
                    current_path = current_root / directory_name

                    parsed_name = self.parse_one(
                        current_path.name,
                        workspace_macros,
                    )

                    if not isinstance(parsed_name, str):
                        raise TypeError(
                            "parsed directory name must be a string",
                        )

                    if parsed_name != current_path.name:
                        current_path.rename(
                            current_path.with_name(parsed_name),
                        )

            return True

    _MacrosManager = __MacrosManager
    _allocate_module = lambda: None


def MacrosManager():
    if _MacrosManager is None:
        _allocate_module()

    return _MacrosManager

# MacrosManager
