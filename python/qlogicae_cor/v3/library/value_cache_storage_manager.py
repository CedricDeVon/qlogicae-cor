__all__ = (
    "ValueCacheStorageManager",
)

_ValueCacheStorageManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _ValueCacheStorageManager

    class __ValueCacheStorageManager:
        __slots__ = (
            "_values",
            "_defaults",
        )

        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        def construct(self):
            global _ExternalDependencyManager

            from .external_dependency_manager import (
                ExternalDependencyManager,
            )

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            self._values = {}
            self._defaults = {}

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            values = kwargs.get("values", {})
            defaults = kwargs.get("defaults", {})

            if values is None:
                values = {}

            if defaults is None:
                defaults = {}

            if not isinstance(values, dict):
                raise ValueError(
                    "'kwargs.values' must be a dictionary"
                )

            if not isinstance(defaults, dict):
                raise ValueError(
                    "'kwargs.defaults' must be a dictionary"
                )

            self._values = values
            self._defaults = defaults

            return True

        def shutdown(self):
            return True

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def values(self):
            return self._values

        @values.setter
        def values(self, value):
            if not isinstance(value, dict):
                raise ValueError("'values' must be a dictionary")

            self._values = value

        @property
        def defaults(self):
            return self._defaults

        @defaults.setter
        def defaults(self, value):
            if not isinstance(value, dict):
                raise ValueError("'defaults' must be a dictionary")

            self._defaults = value

        def _normalize_keys(self, **kwargs):
            keys = kwargs.get("keys")

            if isinstance(keys, str):
                return (keys,)

            if isinstance(keys, (tuple, list)):
                if not keys:
                    raise ValueError("'keys' cannot be empty")

                return tuple(keys)

            raise ValueError(
                "'keys' must be a string, tuple, or list"
            )

        def _normalize_typename(self, **kwargs):
            typename = kwargs.get("typename", "values")

            if typename not in ("values", "defaults"):
                raise ValueError(
                    "'typename' must be either 'values' or 'defaults'"
                )

            return typename

        def read_specified_cache(self, **kwargs):
            typename = self._normalize_typename(**kwargs)

            if typename == "values":
                return self._values

            return self._defaults

        def _get_item_from_cache(self, **kwargs):
            keys = kwargs["keys"]
            typename = kwargs["typename"]

            cache = self.read_specified_cache(
                typename=typename,
            )

            for key in keys:
                if isinstance(cache, dict):
                    if key not in cache:
                        return False, None

                elif isinstance(cache, (list, tuple)):
                    if not isinstance(key, int):
                        return False, None

                    if key < 0 or key >= len(cache):
                        return False, None

                else:
                    return False, None

                cache = cache[key]

            return True, cache

        def _get_item(self, **kwargs):
            keys = self._normalize_keys(
                keys=kwargs.get("keys"),
            )

            typename = self._normalize_typename(
                typename=kwargs.get("typename", "values"),
            )

            found, item = self._get_item_from_cache(
                keys=keys,
                typename=typename,
            )

            if found or typename == "defaults":
                return found, item

            return self._get_item_from_cache(
                keys=keys,
                typename="defaults",
            )

        def is_key_item_found(self, **kwargs):
            found, _ = self._get_item(
                keys=kwargs.get("keys"),
                typename=kwargs.get("typename", "values"),
            )

            return found

        def get_one_item(self, **kwargs):
            found, item = self._get_item(
                keys=kwargs.get("keys"),
                typename=kwargs.get("typename", "values"),
            )

            return item if found else None

        def _get_parent(self, **kwargs):
            keys = self._normalize_keys(
                keys=kwargs.get("keys"),
            )

            typename = self._normalize_typename(
                typename=kwargs.get("typename", "values"),
            )

            create_missing = kwargs.get(
                "create_missing",
                True,
            )

            cache = self.read_specified_cache(
                typename=typename,
            )

            for key in keys[:-1]:
                if isinstance(cache, dict):
                    if key not in cache:
                        if not create_missing:
                            return None, None

                        cache[key] = {}

                    elif not isinstance(
                        cache[key],
                        (dict, list),
                    ):
                        return None, None

                    cache = cache[key]

                elif isinstance(cache, list):
                    if not isinstance(key, int):
                        raise TypeError(
                            f"expected an index, got "
                            f"'{type(key).__name__}'"
                        )

                    if key < 0 or key >= len(cache):
                        raise IndexError(
                            f"Index '{key}' is out of range"
                        )

                    cache = cache[key]

                else:
                    return None, None

            return cache, keys[-1]

        def set_one_item(self, **kwargs):
            keys = kwargs.get("keys")
            value = kwargs.get("value")

            typename = self._normalize_typename(
                typename=kwargs.get("typename", "values"),
            )

            parent, key = self._get_parent(
                keys=keys,
                typename=typename,
                create_missing=kwargs.get(
                    "create_missing",
                    True,
                ),
            )

            if parent is None:
                return False

            if isinstance(parent, dict):
                parent[key] = value

            elif isinstance(parent, list):
                if not isinstance(key, int):
                    raise TypeError(
                        f"expected an index, got "
                        f"'{type(key).__name__}'"
                    )

                if key < 0 or key >= len(parent):
                    raise IndexError(
                        f"Index '{key}' is out of range"
                    )

                parent[key] = value

            else:
                return False

            return True

        def remove_one_item(self, **kwargs):
            typename = self._normalize_typename(
                typename=kwargs.get("typename", "values"),
            )

            parent, key = self._get_parent(
                keys=kwargs.get("keys"),
                typename=typename,
                create_missing=False,
            )

            if parent is None:
                return False

            if isinstance(parent, dict):
                if key not in parent:
                    return False

                del parent[key]

            elif isinstance(parent, list):
                if not isinstance(key, int):
                    raise TypeError(
                        f"expected an index, got "
                        f"'{type(key).__name__}'"
                    )

                if key < 0 or key >= len(parent):
                    return False

                del parent[key]

            else:
                return False

            return True

        def remove_all_items(self, **kwargs):
            cache = self.read_specified_cache(
                typename=kwargs.get("typename", "values"),
            )

            cache.clear()

            return True

        def display_one_item(self, **kwargs):
            found, item = self._get_item(
                keys=kwargs.get("keys"),
                typename=kwargs.get("typename", "values"),
            )

            if not found:
                return False

            _json = (
                _ExternalDependencyManager()
                .import_module(path="json")
            )

            print(
                _json().dumps(
                    item,
                    indent=2,
                    sort_keys=False,
                    ensure_ascii=False,
                    default=str,
                )
            )

            return True

        def display_all_items(self, **kwargs):
            cache = self.read_specified_cache(
                typename=kwargs.get("typename", "values"),
            )

            _json = (
                _ExternalDependencyManager()
                .import_module(path="json")
            )

            print(
                _json().dumps(
                    cache,
                    indent=2,
                    sort_keys=False,
                    ensure_ascii=False,
                    default=str,
                )
            )

            return True

    _ValueCacheStorageManager = __ValueCacheStorageManager
    _allocate = lambda: None


def ValueCacheStorageManager():
    if _ValueCacheStorageManager is None:
        _allocate()

    return _ValueCacheStorageManager
