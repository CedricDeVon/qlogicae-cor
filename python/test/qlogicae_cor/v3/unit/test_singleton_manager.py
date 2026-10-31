import pytest

from qlogicae_cor.v3.library.singleton_manager import (
    SingletonManager,
)


class DummyClass:
    def __init__(self) -> None:
        self.value = 10


class AnotherDummyClass:
    def __init__(self) -> None:
        self.value = 20


class FailingConstructor:
    def __new__(cls):
        raise RuntimeError("failure")


@pytest.fixture(autouse=True)
def reset_manager():
    SingletonManager().reset()
    yield
    SingletonManager().reset()


def test_constructor():
    manager = SingletonManager()

    assert manager is not None


def test_reset_success():
    SingletonManager().get_singleton(
        DummyClass,
    )

    SingletonManager().get_singleton_from_pool(
        DummyClass,
        4,
        0,
    )

    assert len(SingletonManager()._singletons) == 1
    assert len(SingletonManager()._singleton_arrays) == 1

    result = SingletonManager().reset()

    assert result is True
    assert len(SingletonManager()._singletons) == 0
    assert len(SingletonManager()._singleton_arrays) == 0


def test_get_singleton_returns_same_instance():
    instance1 = SingletonManager().get_singleton(
        DummyClass,
    )

    instance2 = SingletonManager().get_singleton(
        DummyClass,
    )

    assert instance1 is instance2


def test_get_singleton_different_constructor():
    instance1 = SingletonManager().get_singleton(
        DummyClass,
    )

    instance2 = SingletonManager().get_singleton(
        AnotherDummyClass,
    )

    assert instance1 is not instance2


def test_get_singleton_preserves_values():
    instance = SingletonManager().get_singleton(
        DummyClass,
    )

    instance.value = 123

    instance2 = SingletonManager().get_singleton(
        DummyClass,
    )

    assert instance2.value == 123


def test_get_singleton_constructor_failure():
    with pytest.raises(Exception):
        SingletonManager().get_singleton(
            FailingConstructor,
        )


def test_get_singleton_pool_returns_same_instance():
    instance1 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        5,
        2,
    )

    instance2 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        5,
        2,
    )

    assert instance1 is instance2


def test_get_singleton_pool_returns_different_indices():
    instance1 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        5,
        0,
    )

    instance2 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        5,
        1,
    )

    assert instance1 is not instance2


def test_get_singleton_pool_wraps_index():
    instance1 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        3,
        0,
    )

    instance2 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        3,
        3,
    )

    assert instance1 is instance2


def test_get_singleton_pool_negative_index():
    instance1 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        3,
        -1,
    )

    instance2 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        3,
        1,
    )

    assert instance1 is not None
    assert instance2 is not None


def test_get_singleton_pool_zero_count():
    with pytest.raises(Exception):
        SingletonManager().get_singleton_from_pool(
            DummyClass,
            0,
            0,
        )


def test_get_singleton_pool_negative_count():
    with pytest.raises(Exception):
        SingletonManager().get_singleton_from_pool(
            DummyClass,
            -5,
            0,
        )


def test_get_singleton_pool_constructor_failure():
    with pytest.raises(Exception):
        SingletonManager().get_singleton_from_pool(
            FailingConstructor,
            3,
            0,
        )


def test_reset_creates_new_singleton():
    instance1 = SingletonManager().get_singleton(
        DummyClass,
    )

    SingletonManager().reset()

    instance2 = SingletonManager().get_singleton(
        DummyClass,
    )

    assert instance1 is not instance2


def test_reset_creates_new_pool():
    instance1 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        2,
        0,
    )

    SingletonManager().reset()

    instance2 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        2,
        0,
    )

    assert instance1 is not instance2


def test_pool_size_created_once():
    SingletonManager().get_singleton_from_pool(
        DummyClass,
        5,
        0,
    )

    assert len(SingletonManager()._singleton_arrays[DummyClass]) == 5


def test_multiple_pools_are_independent():
    SingletonManager().get_singleton_from_pool(
        DummyClass,
        2,
        0,
    )

    SingletonManager().get_singleton_from_pool(
        AnotherDummyClass,
        4,
        0,
    )

    assert len(SingletonManager()._singleton_arrays) == 2


def test_multiple_singletons_are_independent():
    SingletonManager().get_singleton(
        DummyClass,
    )

    SingletonManager().get_singleton(
        AnotherDummyClass,
    )

    assert len(SingletonManager()._singletons) == 2


def test_pool_index_large_number():
    instance1 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        4,
        100,
    )

    instance2 = SingletonManager().get_singleton_from_pool(
        DummyClass,
        4,
        0,
    )

    assert instance1 is instance2

