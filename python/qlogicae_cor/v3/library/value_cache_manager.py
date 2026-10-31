__all__ = (
    "ValueCacheManager",
)

_FilesystemManager = None
_PythonRuntimeUtilityManager = None
_TargetCacheValue = None
_ValueCacheStorageManager = None
_ValueCacheManager = None


def _allocate_module():
    global _allocate_module
    global _FilesystemManager
    global _PythonRuntimeUtilityManager
    global _TargetCacheValue
    global _ValueCacheStorageManager
    global _ValueCacheManager

    from .filesystem_manager import FilesystemManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .target_cache_value import TargetCacheValue
    from .value_cache_storage_manager import ValueCacheStorageManager

    _FilesystemManager = FilesystemManager().get_singleton
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _TargetCacheValue = TargetCacheValue()
    _ValueCacheStorageManager = ValueCacheStorageManager().get_singleton

    class __ValueCacheManager:
        _singleton = None

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _FilesystemManager()
                _ValueCacheStorageManager()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def is_key_found(
            self,
            key_path,
        ):
            result = _ValueCacheStorageManager().is_key_found(key_path)

            return result

        def get_one_value(
            self,
            key_path,
            output_type=None,
        ):
            if output_type is None:
                output_type = _TargetCacheValue.DEFINED

            value = _ValueCacheStorageManager().get_one_value(key_path)

            self.throw_if_value_is_explicitly_invalid(
                value,
                output_type,
            )

            return value

        def set_one_value(
            self,
            key_path,
            value,
            output_type=None,
        ):
            if output_type is None:
                output_type = _TargetCacheValue.DEFINED

            self.throw_if_value_is_explicitly_invalid(
                value,
                output_type,
            )

            result = _ValueCacheStorageManager().set_one_value(
                key_path,
                value,
            )

            return result

        def remove_one_value(
            self,
            key_path,
        ):
            self.throw_if_key_not_found(key_path)

            result = _ValueCacheStorageManager().remove_one_value(key_path)

            return result

        def clear_all_values(self):
            result = _ValueCacheStorageManager().clear_all_values()

            return result

        def display_all_items(self):
            result = _ValueCacheStorageManager().display_all_items()

            return result

        def throw_if_value_is_explicitly_invalid(
            self,
            value,
            output_type=None,
        ):
            if output_type is None:
                output_type = _TargetCacheValue.DEFINED

            match output_type:
                case _TargetCacheValue.FILESYSTEM_PATH:
                    _FilesystemManager().throw_if_filesystem_path_invalid(
                        value,
                    )

                    return True

                case _TargetCacheValue.FILE_PATH:
                    _FilesystemManager().throw_if_file_path_invalid(
                        value,
                    )

                    return True

                case _TargetCacheValue.FOLDER_PATH:
                    _FilesystemManager().throw_if_folder_path_invalid(
                        value,
                    )

                    return True

                case _TargetCacheValue.DEFINED:
                    self.throw_if_undefined(value)

                    return True

                case _:
                    return False

        def throw_if_key_not_found(
            self,
            key_path,
        ):
            if not _ValueCacheStorageManager().is_key_found(key_path):
                raise KeyError(
                    f"key path '{key_path}' does not exist",
                )

            return False

        def throw_if_undefined(
            self,
            value,
        ):
            if value is None:
                raise KeyError("value is not defined")

            return False

    _ValueCacheManager = __ValueCacheManager
    _allocate_module = lambda: None


def ValueCacheManager():
    if _ValueCacheManager is None:
        _allocate_module()

    return _ValueCacheManager


# ValueCacheManager()
