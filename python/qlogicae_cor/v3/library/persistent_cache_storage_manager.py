__all__ = (
    "PersistentCacheStorageManager",
)

_dbm_gnu = None
_pickle = None
_time = None
_PersistentCacheStorageManager = None


def _allocate_module():
    global _allocate_module
    global _dbm_gnu
    global _pickle
    global _time
    global _PersistentCacheStorageManager

    import pickle  # nosec B403
    import time  # nosec B110
    from dbm import gnu

    _dbm_gnu = gnu
    _pickle = pickle
    _time = time

    class __PersistentCacheStorageManager:
        __slots__ = (
            "_database",
            "_database_path",
            "_create_missing",
            "_lifespan_in_seconds",
            "_file_mode",
            "_key_encoding",
            "_pickle_protocol",
            "_auto_remove_expired",
            "_auto_remove_invalid",
            "_sync_on_write",
        )

        _singleton = None

        def __init__(self):
            self._database = None

            self._database_path = "cache.db"
            self._create_missing = True
            self._lifespan_in_seconds = 0.0
            self._file_mode = 0o600
            self._key_encoding = "utf-8"
            self._pickle_protocol = _pickle.HIGHEST_PROTOCOL
            self._auto_remove_expired = True
            self._auto_remove_invalid = True
            self._sync_on_write = False

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def __exit__(self):
            self.close()

        def __del__(self):
            database = self._database

            if database is not None:
                try:
                    database.close()
                except Exception: # nosec B110
                    pass

                self._database = None

        @property
        def is_open(self):
            return self._database is not None

        @property
        def database_path(self):
            return self._database_path

        @database_path.setter
        def database_path(self, value):
            if not isinstance(value, str):
                raise TypeError(
                    "'database_path' must be a string",
                )

            self._ensure_closed()
            self._database_path = value

        @property
        def create_missing(self):
            return self._create_missing

        @create_missing.setter
        def create_missing(self, value):
            if not isinstance(value, bool):
                raise TypeError(
                    "'create_missing' must be a boolean",
                )

            self._ensure_closed()
            self._create_missing = value

        @property
        def lifespan_in_seconds(self):
            return self._lifespan_in_seconds

        @lifespan_in_seconds.setter
        def lifespan_in_seconds(self, value):
            if not isinstance(value, (int, float)):
                raise TypeError(
                    "'lifespan_in_seconds' must be a number",
                )

            if value < 0:
                raise ValueError(
                    "'lifespan_in_seconds' must be >= 0",
                )

            self._lifespan_in_seconds = float(value)

        @property
        def file_mode(self):
            return self._file_mode

        @file_mode.setter
        def file_mode(self, value):
            if not isinstance(value, int):
                raise TypeError(
                    "'file_mode' must be an integer",
                )

            if value < 0 or value > 0o777:
                raise ValueError(
                    "'file_mode' must be between 0 and 0o777",
                )

            self._ensure_closed()
            self._file_mode = value

        @property
        def key_encoding(self):
            return self._key_encoding

        @key_encoding.setter
        def key_encoding(self, value):
            if not isinstance(value, str):
                raise TypeError(
                    "'key_encoding' must be a string",
                )

            try:
                "".encode(value)
            except LookupError as exception:
                raise ValueError(
                    f"unknown encoding: '{value}'",
                ) from exception

            self._key_encoding = value

        @property
        def pickle_protocol(self):
            return self._pickle_protocol

        @pickle_protocol.setter
        def pickle_protocol(self, value):
            if not isinstance(value, int):
                raise TypeError(
                    "'pickle_protocol' must be an integer",
                )

            if not (
                0
                <= value
                <= _pickle.HIGHEST_PROTOCOL
            ):
                raise ValueError(
                    "'pickle_protocol' is outside the supported range",
                )

            self._pickle_protocol = value

        @property
        def auto_remove_expired(self):
            return self._auto_remove_expired

        @auto_remove_expired.setter
        def auto_remove_expired(self, value):
            if not isinstance(value, bool):
                raise TypeError(
                    "'auto_remove_expired' must be a boolean",
                )

            self._auto_remove_expired = value

        @property
        def auto_remove_invalid(self):
            return self._auto_remove_invalid

        @auto_remove_invalid.setter
        def auto_remove_invalid(self, value):
            if not isinstance(value, bool):
                raise TypeError(
                    "'auto_remove_invalid' must be a boolean",
                )

            self._auto_remove_invalid = value

        @property
        def sync_on_write(self):
            return self._sync_on_write

        @sync_on_write.setter
        def sync_on_write(self, value):
            if not isinstance(value, bool):
                raise TypeError(
                    "'sync_on_write' must be a boolean",
                )

            self._sync_on_write = value

        def _ensure_closed(self):
            if self._database is not None:
                raise RuntimeError(
                    "database must be closed before changing "
                    "database configuration",
                )

        def _require_database(self):
            database = self._database

            if database is None:
                raise RuntimeError(
                    "database is not open",
                )

            return database

        def open(self):
            if self._database is not None:
                return False

            self._database = _dbm_gnu.open(
                self.database_path,
                "c" if self.create_missing else "r",
                self.file_mode,
            )

            return True

        def close(self):
            database = self._database

            if database is None:
                return False

            try:
                database.close()
            finally:
                self._database = None

            return True

        def _sync_database(self, database):
            if self.sync_on_write:
                database.sync()

        def _encode_key(self, key_path):
            if not isinstance(key_path, str):
                raise TypeError(
                    "'key_path' must be a string",
                )

            return key_path.encode(
                self.key_encoding,
            )

        def _decode_key(self, key_path):
            return key_path.decode(
                self.key_encoding,
            )

        def _serialize(self, value):
            return _pickle.dumps(
                value,
                protocol=self.pickle_protocol,
            )

        @staticmethod
        def _deserialize(value):
            return _pickle.loads(value)

        def _is_expired(self, created_at, current_time):
            if self.lifespan_in_seconds <= 0:
                return False

            return (
                current_time - created_at
            ) >= self.lifespan_in_seconds

        def _read_item(
            self,
            database,
            encoded_key,
            current_time,
        ):
            if encoded_key not in database:
                return None

            try:
                item = self._deserialize(
                    database[encoded_key],
                )
            except Exception:
                if self.auto_remove_invalid:
                    del database[encoded_key]

                return None

            if not isinstance(item, dict):
                if self.auto_remove_invalid:
                    del database[encoded_key]

                return None

            if (
                "created_at" not in item
                or "value" not in item
            ):
                if self.auto_remove_invalid:
                    del database[encoded_key]

                return None

            created_at = item["created_at"]

            if not isinstance(
                created_at,
                (int, float),
            ):
                if self.auto_remove_invalid:
                    del database[encoded_key]

                return None

            if self._is_expired(
                float(created_at),
                current_time,
            ):
                if self.auto_remove_expired:
                    del database[encoded_key]

                return None

            return item

        def is_keys_found(self, key_paths):
            database = self._require_database()
            current_time = _time.time()
            result = {}

            for key_path in key_paths:
                encoded_key = self._encode_key(
                    key_path,
                )

                result[key_path] = (
                    self._read_item(
                        database,
                        encoded_key,
                        current_time,
                    )
                    is not None
                )

            return result

        def is_key_found(self, key_path):
            return self.is_keys_found(
                (key_path,),
            )[key_path]

        def is_key_expired(self, key_paths):
            database = self._require_database()
            current_time = _time.time()
            result = {}

            for key_path in key_paths:
                encoded_key = self._encode_key(
                    key_path,
                )

                if encoded_key not in database:
                    result[key_path] = None
                    continue

                try:
                    item = self._deserialize(
                        database[encoded_key],
                    )
                except Exception:
                    if self.auto_remove_invalid:
                        del database[encoded_key]

                    result[key_path] = None
                    continue

                if not isinstance(item, dict):
                    if self.auto_remove_invalid:
                        del database[encoded_key]

                    result[key_path] = None
                    continue

                created_at = item.get(
                    "created_at",
                )

                if not isinstance(
                    created_at,
                    (int, float),
                ):
                    if self.auto_remove_invalid:
                        del database[encoded_key]

                    result[key_path] = None
                    continue

                result[key_path] = self._is_expired(
                    float(created_at),
                    current_time,
                )

            return result

        def is_item_expired(self, key_path):
            return self.is_key_expired(
                (key_path,),
            )[key_path]

        def get_many_values(self, key_paths):
            database = self._require_database()
            current_time = _time.time()
            result = {}

            for key_path in key_paths:
                encoded_key = self._encode_key(
                    key_path,
                )

                item = self._read_item(
                    database,
                    encoded_key,
                    current_time,
                )

                if item is None:
                    result[key_path] = None
                else:
                    result[key_path] = item["value"]

            return result

        def get_one_value(self, key_path):
            return self.get_many_values(
                (key_path,),
            )[key_path]

        def set_many_values(self, values):
            database = self._require_database()
            created_at = _time.time()

            for key_path, value in values.items():
                encoded_key = self._encode_key(
                    key_path,
                )

                database[encoded_key] = self._serialize(
                    {
                        "created_at": created_at,
                        "value": value,
                    },
                )

            self._sync_database(database)

            return True

        def set_one_value(self, key_path, value):
            return self.set_many_values(
                {
                    key_path: value,
                },
            )

        def remove_many_values(self, key_paths):
            database = self._require_database()
            result = {}

            for key_path in key_paths:
                encoded_key = self._encode_key(
                    key_path,
                )

                if encoded_key not in database:
                    result[key_path] = False
                    continue

                del database[encoded_key]
                result[key_path] = True

            self._sync_database(database)

            return result

        def remove_one_value(self, key_path):
            return self.remove_many_values(
                (key_path,),
            )[key_path]

        def clear_all_values(self):
            database = self._require_database()

            for key in tuple(database.keys()):
                del database[key]

            self._sync_database(database)

            return True

        def remove_expired_values(self):
            database = self._require_database()
            current_time = _time.time()
            removed = 0

            for encoded_key in tuple(database.keys()):
                try:
                    item = self._deserialize(
                        database[encoded_key],
                    )
                except Exception:
                    if self.auto_remove_invalid:
                        del database[encoded_key]
                        removed += 1

                    continue

                if not isinstance(item, dict):
                    if self.auto_remove_invalid:
                        del database[encoded_key]
                        removed += 1

                    continue

                created_at = item.get(
                    "created_at",
                )

                if not isinstance(
                    created_at,
                    (int, float),
                ):
                    if self.auto_remove_invalid:
                        del database[encoded_key]
                        removed += 1

                    continue

                if self._is_expired(
                    float(created_at),
                    current_time,
                ):
                    del database[encoded_key]
                    removed += 1

            self._sync_database(database)

            return removed

        def reorganize(self):
            database = self._require_database()
            database.reorganize()

            return True

        def sync(self):
            database = self._require_database()
            database.sync()

            return True

        def display_many_items(self, key_paths):
            values = self.get_many_values(
                key_paths,
            )

            for key_path, value in values.items():
                print(
                    {
                        "key": key_path,
                        "value": value,
                    },
                )

            return True

        def display_one_item(self, key_path):
            return self.display_many_items(
                (key_path,),
            )

        def display_all_items(self):
            database = self._require_database()
            current_time = _time.time()

            for encoded_key in tuple(database.keys()):
                key_path = self._decode_key(
                    encoded_key,
                )

                item = self._read_item(
                    database,
                    encoded_key,
                    current_time,
                )

                if item is None:
                    continue

                print(
                    {
                        "key": key_path,
                        "value": item["value"],
                    },
                )

            return True

    _PersistentCacheStorageManager = __PersistentCacheStorageManager
    _allocate_module = lambda: None


def PersistentCacheStorageManager():
    if _PersistentCacheStorageManager is None:
        _allocate_module()

    return _PersistentCacheStorageManager


# PersistentCacheStorageManager()
