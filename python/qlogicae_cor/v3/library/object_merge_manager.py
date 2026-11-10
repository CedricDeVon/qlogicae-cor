__all__ = (
    "ObjectMergeManager",
)

_copy = None
_ObjectMergeManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _ObjectMergeManager

    class __ObjectMergeManager:
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
            global _copy
            global _ExternalDependencyManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )
            _copy = (
                _ExternalDependencyManager()
                    .import_module(
                        path="copy"
                    )
            )

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def deep_merge(
            self,
            left,
            right,
        ):
            if left is None:
                return _copy().deepcopy(right)

            if right is None:
                return _copy().deepcopy(left)

            if isinstance(left, dict) and isinstance(right, dict):
                result = _copy().deepcopy(left)

                for key, value in right.items():
                    if key in result:
                        result[key] = self.deep_merge(
                            result[key],
                            value,
                        )
                    else:
                        result[key] = _copy().deepcopy(value)

                return result

            if isinstance(left, list) and isinstance(right, list):
                return _copy().deepcopy(left) + _copy().deepcopy(right)

            return _copy().deepcopy(right)

        def deep_merge_fragments(
            self,
            left,
            right,
        ):
            if left is None:
                return _copy().deepcopy(right)

            if right is None:
                return _copy().deepcopy(left)

            if isinstance(left, dict) and isinstance(right, dict):
                result = _copy().deepcopy(left)

                for key, value in right.items():
                    if key in result:
                        result[key] = self.deep_merge_fragments(
                            result[key],
                            value,
                        )
                    else:
                        result[key] = _copy().deepcopy(value)

                return result

            if isinstance(left, list) and isinstance(right, list):
                return _copy().deepcopy(right)

            return _copy().deepcopy(right)


    _ObjectMergeManager = __ObjectMergeManager
    _allocate = lambda: None


def ObjectMergeManager():
    if _ObjectMergeManager is None:
        _allocate()

    return _ObjectMergeManager


# ObjectMergeManager()
