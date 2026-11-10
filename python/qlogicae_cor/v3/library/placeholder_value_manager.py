__all__ = (
    "PlaceholderValueManager",
)

_PlaceholderValueManager = None


def _allocate():
    global _allocate
    global _PlaceholderValueManager

    class __PlaceholderValueManager:
        __slots__ = (
            "_none",
            "_not_a_number",
            "_redacted",
            "_expunged",
        )

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

        @property
        def none(self):
            return self._none

        @none.setter
        def none(self, value):
            self._none = value

        @property
        def not_a_number(self):
            return self._not_a_number

        @not_a_number.setter
        def not_a_number(self, value):
            self._not_a_number = value

        @property
        def redacted(self):
            return self._redacted

        @redacted.setter
        def redacted(self, value):
            self._redacted = value

        @property
        def expunged(self):
            return self._expunged

        @expunged.setter
        def expunged(self, value):
            self._expunged = value

        def construct(self):
            self._none = "none"
            self._not_a_number = "nan"
            self._redacted = "redacted"
            self._expunged = "expunged"

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def shutdown(self):
            return True


    _PlaceholderValueManager = __PlaceholderValueManager
    _allocate = lambda: None


def PlaceholderValueManager():
    if _PlaceholderValueManager is None:
        _allocate()

    return _PlaceholderValueManager


# PlaceholderValueManager()

