import asyncio
import threading

import pytest

from qlogicae_cor.v3.library.asynchronous_manager import AsynchronousManager


def add_values(left, right):
    return left + right


def multiply_values(left, right):
    return left * right


def identity(value):
    return value


def raise_value_error():
    raise ValueError("expected error")


def raise_runtime_error(value):
    raise RuntimeError(value)


@pytest.fixture
def manager_type():
    manager_class = AsynchronousManager()
    previous_singleton = manager_class._singleton
    manager_class._singleton = None

    yield manager_class

    instance = manager_class._singleton

    if instance is not None:
        instance.shutdown()

    manager_class._singleton = previous_singleton


@pytest.fixture
def manager(manager_type):
    instance = manager_type()

    yield instance

    instance.shutdown()


class TestAsynchronousManagerAllocation:
    def test_should_return_manager_class(self):
        manager_class = AsynchronousManager()

        assert isinstance(manager_class, type)
        assert callable(manager_class)

    def test_should_return_same_manager_class(self):
        first = AsynchronousManager()
        second = AsynchronousManager()

        assert first is second

    def test_should_allocate_manager_instance(self, manager_type):
        instance = manager_type()

        assert isinstance(instance, manager_type)
        assert instance._thread_executor is None
        assert instance._process_executor is None

        instance.shutdown()

    def test_should_initialize_external_dependencies(self, manager):
        import qlogicae_cor.v3.library.asynchronous_manager as module

        assert callable(module._ExternalDependencyManager)
        assert callable(module._asyncio)
        assert callable(module._threading)
        assert callable(module._functools)
        assert callable(module._concurrent_futures)

    def test_should_construct_manager(self, manager):
        assert manager.construct() is True
        assert manager._thread_executor is None
        assert manager._process_executor is None

    def test_should_support_context_manager(self, manager_type):
        with manager_type() as instance:
            assert instance._thread_executor is None
            assert instance._process_executor is None

    def test_should_shutdown_after_context_manager_exception(
        self,
        manager_type,
    ):
        with pytest.raises(RuntimeError, match="context failure"):
            with manager_type() as instance:
                instance.thread_executor
                raise RuntimeError("context failure")

        assert instance._thread_executor is None

    def test_should_return_singleton(self, manager_type):
        first = manager_type.get_singleton()
        second = manager_type.get_singleton()

        assert first is second

    def test_should_create_new_singleton_after_reset(self, manager_type):
        first = manager_type.get_singleton()
        manager_type._singleton = None
        second = manager_type.get_singleton()

        assert first is not second
        assert manager_type.get_singleton() is second

        first.shutdown()
        second.shutdown()


class TestAsynchronousManagerSetup:
    def test_should_throw_without_arguments(self, manager):
        with pytest.raises(ValueError):
            manager.setup()

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"enabled": True},
            {"workers": 4},
            {"name": "test"},
            {"enabled": False},
            {"workers": 0},
        ],
    )
    def test_should_return_true_with_arguments(self, manager, kwargs):        
        assert manager.setup(**kwargs) is True

    def test_should_accept_multiple_arguments(self, manager):
        assert manager.setup(
            enabled=True,
            workers=4,
            name="test",
        ) is True


class TestAsynchronousManagerExecutors:
    def test_should_lazily_allocate_thread_executor(self, manager):
        assert manager._thread_executor is None

        executor = manager.thread_executor

        assert executor is not None
        assert manager._thread_executor is executor

    def test_should_reuse_thread_executor(self, manager):
        first = manager.thread_executor
        second = manager.thread_executor

        assert first is second

    def test_should_lazily_allocate_process_executor(self, manager):
        assert manager._process_executor is None

        executor = manager.process_executor

        assert executor is not None
        assert manager._process_executor is executor

    def test_should_reuse_process_executor(self, manager):
        first = manager.process_executor
        second = manager.process_executor

        assert first is second

    def test_should_shutdown_thread_executor(self, manager):
        executor = manager.thread_executor

        assert manager.shutdown() is True
        assert manager._thread_executor is None

        with pytest.raises(RuntimeError, match="cannot schedule new futures"):
            executor.submit(identity, 10)

    def test_should_shutdown_process_executor(self, manager):
        executor = manager.process_executor

        assert manager.shutdown() is True
        assert manager._process_executor is None

        with pytest.raises(RuntimeError):
            executor.submit(identity, 10)

    def test_should_shutdown_both_executors(self, manager):
        thread_executor = manager.thread_executor
        process_executor = manager.process_executor

        assert manager.shutdown() is True
        assert manager._thread_executor is None
        assert manager._process_executor is None

        with pytest.raises(RuntimeError):
            thread_executor.submit(identity, 10)

        with pytest.raises(RuntimeError):
            process_executor.submit(identity, 10)

    @pytest.mark.parametrize("wait", [True, False])
    def test_should_accept_shutdown_wait_argument(self, manager, wait):
        manager.thread_executor
        manager.process_executor

        assert manager.shutdown(wait=wait) is True
        assert manager._thread_executor is None
        assert manager._process_executor is None

    def test_should_support_repeated_shutdown(self, manager):
        assert manager.shutdown() is True
        assert manager.shutdown() is True
        assert manager.shutdown() is True

    def test_should_reallocate_thread_executor_after_shutdown(self, manager):
        first = manager.thread_executor

        manager.shutdown()

        second = manager.thread_executor

        assert second is not first

    def test_should_reallocate_process_executor_after_shutdown(self, manager):
        first = manager.process_executor

        manager.shutdown()

        second = manager.process_executor

        assert second is not first


class TestAsynchronousManagerRunThread:
    @pytest.mark.asyncio
    async def test_should_run_function_in_thread(self, manager):
        result = await manager.run_thread(add_values, 10, 20)

        assert result == 30

    @pytest.mark.asyncio
    async def test_should_forward_keyword_arguments(self, manager):
        result = await manager.run_thread(
            combine_values,
            "alpha",
            "beta",
            separator="-",
        )

        assert result == "alpha-beta"

    @pytest.mark.asyncio
    async def test_should_return_none(self, manager):
        result = await manager.run_thread(lambda: None)

        assert result is None

    @pytest.mark.asyncio
    async def test_should_propagate_function_exception(self, manager):
        with pytest.raises(ValueError, match="expected error"):
            await manager.run_thread(raise_value_error)

    @pytest.mark.asyncio
    async def test_should_propagate_runtime_exception(self, manager):
        with pytest.raises(RuntimeError, match="thread failure"):
            await manager.run_thread(
                raise_runtime_error,
                "thread failure",
            )

    @pytest.mark.asyncio
    async def test_should_execute_concurrent_thread_calls(self, manager):
        results = await asyncio.gather(
            *(
                manager.run_thread(add_values, value, 1)
                for value in range(100)
            )
        )

        assert results == list(range(1, 101))

    @pytest.mark.asyncio
    async def test_should_execute_multiple_iterable_values(self, manager):
        results = await manager.map_thread(
            add_values,
            range(100),
            range(100, 200),
        )

        assert results == [value * 2 + 100 for value in range(100)]

def combine_values(left, right, separator):
    return f"{left}{separator}{right}"

class TestAsynchronousManagerRunThreadPool:
    @pytest.mark.asyncio
    async def test_should_run_function_in_thread_pool(self, manager):
        result = await manager.run_thread_pool(add_values, 10, 20)

        assert result == 30

    @pytest.mark.asyncio
    async def test_should_forward_keyword_arguments(self, manager):
        result = await manager.run_process_pool(
            combine_values,
            "alpha",
            "beta",
            separator="-",
        )

        assert result == "alpha-beta"

    @pytest.mark.asyncio
    async def test_should_return_none(self, manager):
        result = await manager.run_thread_pool(lambda: None)

        assert result is None

    @pytest.mark.asyncio
    async def test_should_propagate_function_exception(self, manager):
        with pytest.raises(ValueError, match="expected error"):
            await manager.run_thread_pool(raise_value_error)

    @pytest.mark.asyncio
    async def test_should_execute_concurrent_thread_pool_calls(self, manager):
        results = await asyncio.gather(
            *(
                manager.run_thread_pool(add_values, value, 1)
                for value in range(100)
            )
        )

        assert results == list(range(1, 101))

    @pytest.mark.asyncio
    async def test_should_map_thread_pool_values(self, manager):
        results = await manager.map_thread_pool(
            add_values,
            range(20),
            range(20, 40),
        )

        assert results == [value * 2 + 20 for value in range(20)]


class TestAsynchronousManagerRunProcessPool:
    @pytest.mark.asyncio
    async def test_should_run_function_in_process_pool(self, manager):
        result = await manager.run_process_pool(add_values, 10, 20)

        assert result == 30

    @pytest.mark.asyncio
    async def test_should_forward_keyword_arguments(self, manager):
        result = await manager.run_process_pool(
            combine_values,
            "alpha",
            "beta",
            separator="-",
        )

        assert result == "alpha-beta"

    @pytest.mark.asyncio
    async def test_should_propagate_function_exception(self, manager):
        with pytest.raises(ValueError, match="expected error"):
            await manager.run_process_pool(raise_value_error)

    @pytest.mark.asyncio
    async def test_should_map_process_pool_values(self, manager):
        results = await manager.map_process_pool(
            add_values,
            range(5),
            range(5, 10),
        )

        assert results == [value * 2 + 5 for value in range(5)]


class TestAsynchronousManagerGather:
    @pytest.mark.asyncio
    async def test_should_gather_coroutine_results(self, manager):
        async def first():
            return 10

        async def second():
            return 20

        results = await manager.gather(first(), second())

        assert results == [10, 20]

    @pytest.mark.asyncio
    async def test_should_preserve_result_order(self, manager):
        async def delayed_result(value, delay):
            await asyncio.sleep(delay)
            return value

        results = await manager.gather(
            delayed_result(1, 0.03),
            delayed_result(2, 0.01),
            delayed_result(3, 0.02),
        )

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_should_return_empty_list_without_coroutines(self, manager):
        assert await manager.gather() == []

    @pytest.mark.asyncio
    async def test_should_propagate_coroutine_exception(self, manager):
        async def failing():
            raise ValueError("gather failure")

        with pytest.raises(ValueError, match="gather failure"):
            await manager.gather(failing())

    @pytest.mark.asyncio
    async def test_should_return_exceptions_when_requested(self, manager):
        async def failing():
            raise ValueError("gather failure")

        results = await manager.gather(
            failing(),
            asyncio.sleep(0, result=20),
            return_exceptions=True,
        )

        assert isinstance(results[0], ValueError)
        assert str(results[0]) == "gather failure"
        assert results[1] == 20

    @pytest.mark.asyncio
    async def test_should_execute_many_coroutines(self, manager):
        async def calculate(value):
            return value * 2

        results = await manager.gather(
            *(calculate(value) for value in range(500))
        )

        assert results == [value * 2 for value in range(500)]


class TestAsynchronousManagerWait:
    @pytest.mark.asyncio
    async def test_should_wait_for_coroutines(self, manager):
        async def first():
            return 10

        async def second():
            return 20

        done, pending = await manager.wait(first(), second())

        assert len(done) == 2
        assert not pending
        assert {task.result() for task in done} == {10, 20}

    @pytest.mark.asyncio
    async def test_should_return_completed_tasks(self, manager):
        async def immediate():
            return "completed"

        done, pending = await manager.wait(immediate())

        assert len(done) == 1
        assert not pending
        assert next(iter(done)).result() == "completed"

    @pytest.mark.asyncio
    async def test_should_return_pending_tasks_after_timeout(self, manager):
        async def delayed():
            await asyncio.sleep(1)
            return "completed"

        done, pending = await manager.wait(
            delayed(),
            timeout=0.01,
        )

        assert not done
        assert len(pending) == 1

        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)

    @pytest.mark.asyncio
    async def test_should_wait_for_multiple_coroutines_with_timeout(self, manager):
        async def delayed(value):
            await asyncio.sleep(0.01)
            return value

        done, pending = await manager.wait(
            delayed(1),
            delayed(2),
            timeout=1,
        )

        assert len(done) == 2
        assert not pending

    @pytest.mark.asyncio
    async def test_should_raise_for_empty_coroutines(self, manager):
        with pytest.raises(ValueError):
            await manager.wait()


class TestAsynchronousManagerCreateTask:
    @pytest.mark.asyncio
    async def test_should_create_task(self, manager):
        async def calculate():
            return 42

        task = manager.create_task(calculate())

        assert isinstance(task, asyncio.Task)
        assert await task == 42

    @pytest.mark.asyncio
    async def test_should_assign_task_name(self, manager):
        async def calculate():
            return 42

        task = manager.create_task(
            calculate(),
            name="calculation-task",
        )

        assert task.get_name() == "calculation-task"
        assert await task == 42

    @pytest.mark.asyncio
    async def test_should_propagate_task_exception(self, manager):
        async def failing():
            raise RuntimeError("task failure")

        task = manager.create_task(failing())

        with pytest.raises(RuntimeError, match="task failure"):
            await task

    @pytest.mark.asyncio
    async def test_should_cancel_task(self, manager):
        started = asyncio.Event()

        async def delayed():
            started.set()
            await asyncio.sleep(10)

        task = manager.create_task(delayed())

        await started.wait()
        assert task.cancel() is True

        with pytest.raises(asyncio.CancelledError):
            await task


class TestAsynchronousManagerTimeout:
    @pytest.mark.asyncio
    async def test_should_return_coroutine_result(self, manager):
        async def calculate():
            return 42

        result = await manager.timeout(calculate(), 1)

        assert result == 42

    @pytest.mark.asyncio
    async def test_should_raise_timeout_error(self, manager):
        async def delayed():
            await asyncio.sleep(1)

        with pytest.raises(asyncio.TimeoutError):
            await manager.timeout(delayed(), 0.01)

    @pytest.mark.asyncio
    async def test_should_propagate_coroutine_exception(self, manager):
        async def failing():
            raise ValueError("timeout failure")

        with pytest.raises(ValueError, match="timeout failure"):
            await manager.timeout(failing(), 1)

    @pytest.mark.asyncio
    async def test_should_handle_zero_timeout(self, manager):
        async def delayed():
            await asyncio.sleep(0.1)
            return 42

        with pytest.raises(asyncio.TimeoutError):
            await manager.timeout(delayed(), 0)


class TestAsynchronousManagerMapThread:
    @pytest.mark.asyncio
    async def test_should_map_single_iterable(self, manager):
        results = await manager.map_thread(identity, range(10))

        assert results == list(range(10))

    @pytest.mark.asyncio
    async def test_should_map_multiple_iterables(self, manager):
        results = await manager.map_thread(
            add_values,
            range(10),
            range(10, 20),
        )

        assert results == [value + value + 10 for value in range(10)]

    @pytest.mark.asyncio
    async def test_should_return_empty_results_for_empty_iterables(self, manager):
        results = await manager.map_thread(identity, ())

        assert results == []

    @pytest.mark.asyncio
    async def test_should_return_empty_results_without_iterables(self, manager):
        results = await manager.map_thread(identity)

        assert results == []

    @pytest.mark.asyncio
    async def test_should_raise_for_unequal_iterable_lengths(self, manager):
        with pytest.raises(ValueError):
            await manager.map_thread(
                add_values,
                (),
                (1,),
            )

    @pytest.mark.asyncio
    async def test_should_execute_stress_mapping(self, manager):
        values = range(500)

        results = await manager.map_thread(
            multiply_values,
            values,
            values,
        )

        assert results == [value * value for value in range(500)]


class TestAsynchronousManagerMapThreadPool:
    @pytest.mark.asyncio
    async def test_should_map_single_iterable(self, manager):
        results = await manager.map_thread_pool(identity, range(10))

        assert results == list(range(10))

    @pytest.mark.asyncio
    async def test_should_map_multiple_iterables(self, manager):
        results = await manager.map_thread_pool(
            add_values,
            range(10),
            range(10, 20),
        )

        assert results == [value + value + 10 for value in range(10)]

    @pytest.mark.asyncio
    async def test_should_return_empty_results_for_empty_iterables(self, manager):
        results = await manager.map_thread_pool(identity, ())

        assert results == []

    @pytest.mark.asyncio
    async def test_should_return_empty_results_without_iterables(self, manager):
        results = await manager.map_thread_pool(identity)

        assert results == []

    @pytest.mark.asyncio
    async def test_should_raise_for_unequal_iterable_lengths(self, manager):
        with pytest.raises(ValueError):
            await manager.map_thread_pool(
                add_values,
                (),
                (1,),
            )

    @pytest.mark.asyncio
    async def test_should_execute_stress_mapping(self, manager):
        values = range(200)

        results = await manager.map_thread_pool(
            multiply_values,
            values,
            values,
        )

        assert results == [value * value for value in range(200)]


class TestAsynchronousManagerMapProcessPool:
    @pytest.mark.asyncio
    async def test_should_map_single_iterable(self, manager):
        results = await manager.map_process_pool(identity, range(5))

        assert results == list(range(5))

    @pytest.mark.asyncio
    async def test_should_map_multiple_iterables(self, manager):
        results = await manager.map_process_pool(
            add_values,
            range(5),
            range(5, 10),
        )

        assert results == [value + value + 5 for value in range(5)]

    @pytest.mark.asyncio
    async def test_should_return_empty_results_for_empty_iterables(self, manager):
        results = await manager.map_process_pool(identity, ())

        assert results == []

    @pytest.mark.asyncio
    async def test_should_return_empty_results_without_iterables(self, manager):
        results = await manager.map_process_pool(identity)

        assert results == []

    @pytest.mark.asyncio
    async def test_should_raise_for_unequal_iterable_lengths(self, manager):
        with pytest.raises(ValueError):
            await manager.map_process_pool(
                add_values,
                (),
                (1,),
            )


class TestAsynchronousManagerCreateThread:
    def test_should_create_and_start_thread(self, manager):
        completed = threading.Event()

        def target():
            completed.set()

        thread = manager.create_thread(target)

        thread.join(timeout=1)

        assert completed.is_set()
        assert not thread.is_alive()

    def test_should_create_thread_without_starting(self, manager):
        completed = threading.Event()

        def target():
            completed.set()

        thread = manager.create_thread(
            target,
            start=False,
        )

        assert not thread.is_alive()
        assert not completed.is_set()

        thread.start()
        thread.join(timeout=1)

        assert completed.is_set()
        assert not thread.is_alive()

    def test_should_forward_positional_arguments(self, manager):
        results = []
        completed = threading.Event()

        def target(value):
            results.append(value)
            completed.set()

        thread = manager.create_thread(target, 42)
        thread.join(timeout=1)

        assert completed.is_set()
        assert results == [42]

    def test_should_forward_keyword_arguments(self, manager):
        results = []
        completed = threading.Event()

        def target(value, multiplier):
            results.append(value * multiplier)
            completed.set()

        thread = manager.create_thread(
            target,
            value=10,
            multiplier=5,
        )

        thread.join(timeout=1)

        assert completed.is_set()
        assert results == [50]

    def test_should_create_daemon_thread(self, manager):
        thread = manager.create_thread(
            identity,
            10,
            start=False,
            daemon=True,
        )

        assert thread.daemon is True
        assert not thread.is_alive()

    def test_should_create_non_daemon_thread(self, manager):
        thread = manager.create_thread(
            identity,
            10,
            start=False,
            daemon=False,
        )

        assert thread.daemon is False
        assert not thread.is_alive()

    def test_should_return_thread_instance(self, manager):
        thread = manager.create_thread(
            identity,
            10,
            start=False,
        )

        assert isinstance(thread, threading.Thread)

    def test_should_allow_multiple_threads(self, manager):
        results = []
        lock = threading.Lock()

        def target(value):
            with lock:
                results.append(value)

        threads = [
            manager.create_thread(target, value)
            for value in range(100)
        ]

        for thread in threads:
            thread.join(timeout=1)

        assert sorted(results) == list(range(100))
        assert all(not thread.is_alive() for thread in threads)


class TestAsynchronousManagerLifecycle:
    def test_should_reset_executors_after_shutdown(self, manager):
        manager.thread_executor
        manager.process_executor

        assert manager._thread_executor is not None
        assert manager._process_executor is not None

        manager.shutdown()

        assert manager._thread_executor is None
        assert manager._process_executor is None

    def test_should_allow_operations_after_shutdown(self, manager):
        manager.thread_executor
        manager.shutdown()

        assert manager.thread_executor is not None

    def test_should_allow_repeated_construct_calls(self, manager):
        assert manager.construct() is True
        assert manager.construct() is True

        assert manager._thread_executor is None
        assert manager._process_executor is None

    def test_should_not_create_executors_during_construction(self, manager):
        assert manager._thread_executor is None
        assert manager._process_executor is None

    def test_should_support_slots(self, manager):
        with pytest.raises(AttributeError):
            manager.unexpected_attribute = True