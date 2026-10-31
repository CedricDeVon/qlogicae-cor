from __future__ import annotations

__all__ = (
    "DiskCacheStorageManager",
)

from typing import (
    Any,
    cast,
)

_dbm_gnu: Any = None
_pickle: Any = None
_time: Any = None


def _handle_dynamic_imports() -> None:
    global _handle_dynamic_imports
    global _dbm_gnu
    global _pickle
    global _time

    import pickle # nosec B403
    import time 
    from dbm import gnu

    _dbm_gnu = gnu
    _pickle = pickle
    _time = time

    _handle_dynamic_imports = lambda: None


class DiskCacheStorageManager:
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

    def __init__(self) -> None:
        _handle_dynamic_imports()

        self._database: Any = None

        self._database_path: str = "cache.db"
        self._create_missing: bool = True
        self._lifespan_in_seconds: float = 0.0
        self._file_mode: int = 0o600
        self._key_encoding: str = "utf-8"
        self._pickle_protocol: int = _pickle.HIGHEST_PROTOCOL
        self._auto_remove_expired: bool = True
        self._auto_remove_invalid: bool = True
        self._sync_on_write: bool = False

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        database = self._database

        if database is not None:
            try:
                database.close()
            except Exception: # nosec B110
                pass # nosec B110

            self._database = None

    @property
    def is_open(self) -> bool:
        return self._database is not None

    @property
    def database_path(self) -> str:
        return self._database_path

    @database_path.setter
    def database_path(
        self,
        value: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                "'database_path' must be a string",
            )

        self._ensure_closed()

        self._database_path = value

    @property
    def create_missing(self) -> bool:
        return self._create_missing

    @create_missing.setter
    def create_missing(
        self,
        value: bool,
    ) -> None:
        if not isinstance(value, bool):
            raise TypeError(
                "'create_missing' must be a boolean",
            )

        self._ensure_closed()

        self._create_missing = value

    @property
    def lifespan_in_seconds(self) -> float:
        return self._lifespan_in_seconds

    @lifespan_in_seconds.setter
    def lifespan_in_seconds(
        self,
        value: float,
    ) -> None:
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
    def file_mode(self) -> int:
        return self._file_mode

    @file_mode.setter
    def file_mode(
        self,
        value: int,
    ) -> None:
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
    def key_encoding(self) -> str:
        return self._key_encoding

    @key_encoding.setter
    def key_encoding(
        self,
        value: str,
    ) -> None:
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
    def pickle_protocol(self) -> int:
        return self._pickle_protocol

    @pickle_protocol.setter
    def pickle_protocol(
        self,
        value: int,
    ) -> None:
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
    def auto_remove_expired(self) -> bool:
        return self._auto_remove_expired

    @auto_remove_expired.setter
    def auto_remove_expired(
        self,
        value: bool,
    ) -> None:
        if not isinstance(value, bool):
            raise TypeError(
                "'auto_remove_expired' must be a boolean",
            )

        self._auto_remove_expired = value

    @property
    def auto_remove_invalid(self) -> bool:
        return self._auto_remove_invalid

    @auto_remove_invalid.setter
    def auto_remove_invalid(
        self,
        value: bool,
    ) -> None:
        if not isinstance(value, bool):
            raise TypeError(
                "'auto_remove_invalid' must be a boolean",
            )

        self._auto_remove_invalid = value

    @property
    def sync_on_write(self) -> bool:
        return self._sync_on_write

    @sync_on_write.setter
    def sync_on_write(
        self,
        value: bool,
    ) -> None:
        if not isinstance(value, bool):
            raise TypeError(
                "'sync_on_write' must be a boolean",
            )

        self._sync_on_write = value

    def _ensure_closed(self) -> None:
        if self._database is not None:
            raise RuntimeError(
                "database must be closed before changing "
                "database configuration",
            )

    def _require_database(self) -> Any:
        database = self._database

        if database is None:
            raise RuntimeError(
                "database is not open",
            )

        return database

    def open(self) -> bool:
        if self._database is not None:
            return False

        self._database = _dbm_gnu.open(
            self.database_path,
            "c" if self.create_missing else "r",
            self.file_mode,
        )

        return True

    def close(self) -> bool:
        database = self._database

        if database is None:
            return False

        try:
            database.close()
        finally:
            self._database = None

        return True

    def _sync_database(
        self,
        database: Any,
    ) -> None:
        if self.sync_on_write:
            database.sync()

    def _encode_key(
        self,
        key_path: str,
    ) -> bytes:
        if not isinstance(key_path, str):
            raise TypeError(
                "'key_path' must be a string",
            )

        return key_path.encode(
            self.key_encoding,
        )

    def _decode_key(
        self,
        key_path: bytes,
    ) -> str:
        return key_path.decode(
            self.key_encoding,
        )

    def _serialize(
        self,
        value: object,
    ) -> bytes:
        return cast(
            bytes,
            _pickle.dumps(
                value,
                protocol=self.pickle_protocol,
            ),
        )

    @staticmethod
    def _deserialize(
        value: bytes,
    ) -> object:
        return _pickle.loads(value)

    def _is_expired(
        self,
        created_at: float,
        current_time: float,
    ) -> bool:
        if self.lifespan_in_seconds <= 0:
            return False

        return (
            current_time - created_at
        ) >= self.lifespan_in_seconds

    def _read_item(
        self,
        database: Any,
        encoded_key: bytes,
        current_time: float,
    ) -> Any:
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

    def is_keys_found(
        self,
        key_paths: tuple[str, ...],
    ) -> dict[str, bool]:
        database = self._require_database()
        current_time = _time.time()
        result: dict[str, bool] = {}

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

    def is_key_found(
        self,
        key_path: str,
    ) -> bool:
        return self.is_keys_found(
            (key_path,),
        )[key_path]

    def is_key_expired(
        self,
        key_paths: tuple[str, ...],
    ) -> dict[str, bool | None]:
        database = self._require_database()
        current_time = _time.time()
        result: dict[str, bool | None] = {}

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

    def is_item_expired(
        self,
        key_path: str,
    ) -> bool | None:
        return self.is_key_expired(
            (key_path,),
        )[key_path]

    def get_many_values(
        self,
        key_paths: tuple[str, ...],
    ) -> dict[str, Any]:
        database = self._require_database()
        current_time = _time.time()
        result: dict[str, Any] = {}

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

    def get_one_value(
        self,
        key_path: str,
    ) -> Any:
        return self.get_many_values(
            (key_path,),
        )[key_path]

    def set_many_values(
        self,
        values: dict[str, object],
    ) -> bool:
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

    def set_one_value(
        self,
        key_path: str,
        value: object,
    ) -> bool:
        return self.set_many_values(
            {
                key_path: value,
            },
        )

    def remove_many_values(
        self,
        key_paths: tuple[str, ...],
    ) -> dict[str, bool]:
        database = self._require_database()
        result: dict[str, bool] = {}

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

    def remove_one_value(
        self,
        key_path: str,
    ) -> bool:
        return self.remove_many_values(
            (key_path,),
        )[key_path]

    def clear_all_values(self) -> bool:
        database = self._require_database()

        for key in tuple(database.keys()):
            del database[key]

        self._sync_database(database)

        return True

    def remove_expired_values(self) -> int:
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

    def reorganize(self) -> bool:
        database = self._require_database()

        database.reorganize()

        return True

    def sync(self) -> bool:
        database = self._require_database()

        database.sync()

        return True

    def display_many_items(
        self,
        key_paths: tuple[str, ...],
    ) -> bool:
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

    def display_one_item(
        self,
        key_path: str,
    ) -> bool:
        return self.display_many_items(
            (key_path,),
        )

    def display_all_items(self) -> bool:
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
