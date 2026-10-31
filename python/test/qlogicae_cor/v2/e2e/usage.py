import importlib
import pkgutil
import sys
import tracemalloc

from qlogicae_cor.v2 import library


def test_tracemalloc_memory() -> None:
    tracemalloc.start()

    for module in pkgutil.walk_packages(
        library.__path__,
        prefix=library.__name__ + ".",
    ):
        print(module.name)

    current, peak = tracemalloc.get_traced_memory()

    print(f"Current: {current / 1024:.2f} KB")
    print(f"Peak: {peak / 1024:.2f} KB")

    tracemalloc.stop()


def test_module_import_memory() -> None:
    tracemalloc.start()

    for module in pkgutil.walk_packages(
        library.__path__,
        prefix=library.__name__ + ".",
    ):
        before = tracemalloc.get_traced_memory()[0]

        importlib.import_module(module.name)

        after = tracemalloc.get_traced_memory()[0]

        print(
            f"{module.name}: "
            f"{(after - before) / 1024:.2f} KB"
        )

    tracemalloc.stop()


def test_object_memory() -> None:
    print(f"Library: {sys.getsizeof(library)} bytes")


def test_process_memory() -> None:
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF)

    print(f"Maximum RSS: {usage.ru_maxrss}")


if __name__ == "__main__":
    test_tracemalloc_memory()
    test_module_import_memory()
    test_object_memory()
    test_process_memory()

