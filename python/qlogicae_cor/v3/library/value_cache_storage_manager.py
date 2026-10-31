__all__ = (
    "ValueCacheStorageManager",
)

_json = None
_ValueCacheStorageManager = None


def _allocate_module():
    global _allocate_module
    global _json
    global _ValueCacheStorageManager

    import json

    _json = json

    class __ValueCacheStorageManager:
        __slots__ = (
            "_collection",
        )

        _singleton = None

        def __init__(self):
            self._collection = {}

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def collection(self):
            return self._collection

        def is_key_found(self, keys):
            if not keys:
                return False

            cache = self._collection

            for key in keys:
                if isinstance(cache, dict):
                    if key not in cache:
                        return False

                elif isinstance(cache, (list, tuple)):
                    if not isinstance(key, int):
                        return False

                    if key < 0 or key >= len(cache):
                        return False

                else:
                    return False

                cache = cache[key]

            return True

        def get_one_value(self, keys):
            if not keys:
                return None

            cache = self._collection

            for key in keys:
                if isinstance(cache, dict):
                    if key not in cache:
                        return None

                elif isinstance(cache, (list, tuple)):
                    if not isinstance(key, int):
                        return None

                    if key < 0 or key >= len(cache):
                        return None

                else:
                    return None

                cache = cache[key]

            return cache

        def set_one_value(
            self,
            keys,
            value,
            create_missing=True,
        ):
            if not keys:
                raise ValueError("'keys' cannot be empty")

            cache = self._collection

            for key in keys[:-1]:
                if isinstance(cache, dict):
                    if key not in cache:
                        if not create_missing:
                            raise KeyError(
                                f"key path '{keys}' not found"
                            )

                        cache[key] = {}

                    elif not isinstance(
                        cache[key],
                        (dict, list),
                    ):
                        raise TypeError(
                            f"key path '{keys}' does not reference "
                            "a dictionary or list"
                        )

                    cache = cache[key]

                elif isinstance(cache, list):
                    if not isinstance(key, int):
                        raise TypeError(
                            f"expected an index, got "
                            f"'{type(key).__name__}'"
                        )

                    if key < 0 or key >= len(cache):
                        raise IndexError(
                            f"index '{key}' is out of range"
                        )

                    cache = cache[key]

                else:
                    raise TypeError(
                        f"cannot traverse into "
                        f"'{type(cache).__name__}'"
                    )

            last = keys[-1]

            if isinstance(cache, dict):
                cache[last] = value

            elif isinstance(cache, list):
                if not isinstance(last, int):
                    raise TypeError(
                        f"expected an index, got "
                        f"{type(last).__name__}"
                    )

                if last < 0 or last >= len(cache):
                    raise IndexError(
                        f"index '{last}' is out of range"
                    )

                cache[last] = value

            else:
                raise TypeError(
                    "destination is neither a "
                    "dictionary nor a list"
                )

            return True

        def remove_one_value(self, keys):
            if not keys:
                raise ValueError(
                    "keys cannot be empty"
                )

            cache = self._collection

            for key in keys[:-1]:
                if isinstance(cache, dict):
                    if key not in cache:
                        raise KeyError(
                            f"key path '{keys}' not found"
                        )

                elif isinstance(cache, list):
                    if not isinstance(key, int):
                        raise TypeError(
                            f"expected an index, got "
                            f"{type(key).__name__}"
                        )

                    if key < 0 or key >= len(cache):
                        raise IndexError(
                            f"index path '{keys}' "
                            "is out of range"
                        )

                else:
                    raise TypeError(
                        f"cannot traverse into "
                        f"'{type(cache).__name__}'"
                    )

                cache = cache[key]

            last = keys[-1]

            if isinstance(cache, dict):
                try:
                    del cache[last]
                except KeyError:
                    raise KeyError(
                        f"key '{last}' not found"
                    ) from None

            elif isinstance(cache, list):
                if not isinstance(last, int):
                    raise TypeError(
                        f"expected an index, got "
                        f"{type(last).__name__}"
                    )

                if last < 0 or last >= len(cache):
                    raise IndexError(
                        f"index '{last}' is out of range"
                    )

                del cache[last]

            else:
                raise TypeError(
                    "destination is neither a "
                    "dictionary nor a list"
                )

            return True

        def clear_all_values(self):
            self._collection.clear()

            return True

        def display_one_item(self, key):
            print(
                f"- {key}: "
                f"{self._collection[key]}"
            )

            return True

        def display_all_items(self):
            print(
                _json.dumps(
                    self._collection,
                    indent=2,
                    sort_keys=False,
                    ensure_ascii=False,
                    default=str,
                )
            )

            return True

    _ValueCacheStorageManager = __ValueCacheStorageManager
    _allocate_module = lambda: None


def ValueCacheStorageManager():
    if _ValueCacheStorageManager is None:
        _allocate_module()

    return _ValueCacheStorageManager


# ValueCacheStorageManager()
