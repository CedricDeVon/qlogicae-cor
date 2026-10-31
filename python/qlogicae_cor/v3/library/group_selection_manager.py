__all__ = (
    "GroupSelectionManager",
)

_GroupSelectionManager = None


def _allocate_module():
    global _allocate_module
    global _GroupSelectionManager

    class __GroupSelectionManager:
        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def flatten_group(
            self,
            target,
            data,
        ):
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
    _allocate_module = lambda: None


def GroupSelectionManager():
    if _GroupSelectionManager is None:
        _allocate_module()

    return _GroupSelectionManager


# GroupSelectionManager()
