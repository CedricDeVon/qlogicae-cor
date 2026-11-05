__all__ = (
    "ValueCacheManager",
)

_FilesystemManager = None
_TargetCacheValue = None
_ValueCacheStorageManager = None
_ValueCacheManager = None
_ExternalDependencyManager = None

def _allocate():
    global _allocate
    global _ValueCacheManager

    class __ValueCacheManager:
        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _FilesystemManager
            global _TargetCacheValue
            global _ValueCacheStorageManager
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _FilesystemManager = (
                _ExternalDependencyManager().import_module(
                    path=".filesystem_manager",
                    package="qlogicae_cor.v3.library",
                    memger="FilesystemManager",
                    is_member_callable=True,
                )
            )
            _TargetCacheValue = (
                _ExternalDependencyManager().import_module(
                    path=".target_cache_value",
                    package="qlogicae_cor.v3.library",
                    memger="TargetCacheValue",
                    is_member_callable=True,
                )
            )
            _ValueCacheStorageManager = (
                _ExternalDependencyManager().import_module(
                    path=".value_cache_storage_manager",
                    package="qlogicae_cor.v3.library",
                    memger="ValueCacheStorageManager",
                    is_member_callable=True,
                )
            )

            return True

        def setup(self, **kwargs):
            if not kwargs:
                return False

            _ValueCacheStorageManager().get_singleton().setup(
                **kwargs
            )

            return True

        def shutdown(self):
            _ValueCacheStorageManager().get_singleton().shutdown()

            return True

        def is_key_found(
            self,
            key_path,
        ):
            result = (
                _ValueCacheStorageManager()
                    .get_singleton()
                    .is_key_found(key_path)
            )

            return result

        def get_one_value(
            self,
            key_path,
            output_type=None,
        ):
            if output_type is None:
                output_type = _TargetCacheValue().DEFINED

            value = (
                _ValueCacheStorageManager().get_singleton()
                    .get_one_value(key_path)
            )

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
                output_type = _TargetCacheValue().DEFINED

            self.throw_if_value_is_explicitly_invalid(
                value,
                output_type,
            )

            result = (
                _ValueCacheStorageManager().get_singleton()
                    .set_one_value(
                        key_path,
                        value,
                    )
            )

            return result

        def remove_one_value(
            self,
            key_path,
        ):
            self.throw_if_key_not_found(key_path)

            result = (
                _ValueCacheStorageManager().get_singleton()
                    .remove_one_value(key_path)
            )

            return result

        def clear_all_values(self):
            result = (
                _ValueCacheStorageManager().get_singleton()
                    .clear_all_values()
            )

            return result

        def display_all_items(self):
            result = (
                _ValueCacheStorageManager().get_singleton()
                    .display_all_items()
            )

            return result

        def throw_if_value_is_explicitly_invalid(
            self,
            value,
            output_type=None,
        ):
            TargetCacheValue = (
                _TargetCacheValue()
            )

            if output_type is None:
                output_type = TargetCacheValue.DEFINED

            match output_type:
                case TargetCacheValue.FILESYSTEM_PATH:
                    _FilesystemManager().get_singleton().throw_if_filesystem_path_invalid(
                        value
                    )

                    return True

                case TargetCacheValue.FILE_PATH:
                    _FilesystemManager().get_singleton().throw_if_file_path_invalid(
                        value
                    )

                    return True

                case TargetCacheValue.FOLDER_PATH:
                    _FilesystemManager().get_singleton().throw_if_folder_path_invalid(
                        value
                    )

                    return True

                case TargetCacheValue.DEFINED:
                    self.throw_if_undefined(value)

                    return True

                case _:
                    return False

        def throw_if_key_not_found(
            self,
            key_path,
        ):
            if not _ValueCacheStorageManager().get_singleton().is_key_found(key_path):
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
    _allocate = lambda: None


def ValueCacheManager():
    if _ValueCacheManager is None:
        _allocate()

    return _ValueCacheManager


# ValueCacheManager().get_singleton()
