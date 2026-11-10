__all__ = (
    "GroupSelectionManager",
)

_GroupSelectionManager = None


def _allocate():
    global _allocate
    global _GroupSelectionManager

    class __GroupSelectionManager:
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
            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True

        def flatten_group(
            self,
            target,
            data,
        ):
            if not target:
                raise ValueError("'target' must be defined")

            if not data:
                raise ValueError("'data' must be defined")

            resolved = []
            visited = set()
            stack = [target]

            while stack:
                value = stack.pop()

                if value in visited:
                    continue

                visited.add(value)

                if value not in data:
                    resolved.append(value)
                    continue

                stack.extend(reversed(data[value]))

            return tuple(resolved)

    _GroupSelectionManager = __GroupSelectionManager
    _allocate = lambda: None


def GroupSelectionManager():
    if _GroupSelectionManager is None:
        _allocate()

    return _GroupSelectionManager


# GroupSelectionManager()

