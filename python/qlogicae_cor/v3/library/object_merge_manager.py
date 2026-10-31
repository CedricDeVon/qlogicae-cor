__all__ = (
    "ObjectMergeManager",
)

_deepcopy = None
_ObjectMergeManager = None


def _allocate_module():
    global _allocate_module
    global _deepcopy
    global _ObjectMergeManager

    from copy import deepcopy

    _deepcopy = deepcopy

    class __ObjectMergeManager:
        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def deep_merge(
            self,
            left,
            right,
        ):
            if left is None:
                return _deepcopy(right)

            if right is None:
                return _deepcopy(left)

            if isinstance(left, dict) and isinstance(right, dict):
                result = _deepcopy(left)

                for key, value in right.items():
                    if key in result:
                        result[key] = self.deep_merge(
                            result[key],
                            value,
                        )
                    else:
                        result[key] = _deepcopy(value)

                return result

            if isinstance(left, list) and isinstance(right, list):
                return _deepcopy(left) + _deepcopy(right)

            return _deepcopy(right)

        def deep_merge_fragments(
            self,
            left,
            right,
        ):
            if left is None:
                return _deepcopy(right)

            if right is None:
                return _deepcopy(left)

            if isinstance(left, dict) and isinstance(right, dict):
                result = _deepcopy(left)

                for key, value in right.items():
                    if key in result:
                        result[key] = self.deep_merge_fragments(
                            result[key],
                            value,
                        )
                    else:
                        result[key] = _deepcopy(value)

                return result

            if isinstance(left, list) and isinstance(right, list):
                return _deepcopy(right)

            return _deepcopy(right)

    _ObjectMergeManager = __ObjectMergeManager
    _allocate_module = lambda: None


def ObjectMergeManager():
    if _ObjectMergeManager is None:
        _allocate_module()

    return _ObjectMergeManager


# ObjectMergeManager()
