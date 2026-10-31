__all__ = (
    "AsynchronousManager",
)

_asyncio = None
_threading = None
_partial = None
_ProcessPoolExecutor = None
_ThreadPoolExecutor = None
_AsynchronousManager = None


def _allocate_module():
    global _allocate_module
    global _asyncio
    global _threading
    global _partial
    global _ProcessPoolExecutor
    global _ThreadPoolExecutor
    global _AsynchronousManager

    import asyncio
    import threading
    from concurrent.futures import (
        ProcessPoolExecutor,
        ThreadPoolExecutor,
    )
    from functools import partial

    _asyncio = asyncio
    _threading = threading
    _partial = partial
    _ProcessPoolExecutor = ProcessPoolExecutor
    _ThreadPoolExecutor = ThreadPoolExecutor

    class __AsynchronousManager:
        __slots__ = (
            "_thread_executor",
            "_process_executor",
        )

        _singleton = None

        def __init__(self):
            self._thread_executor = None
            self._process_executor = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        @property
        def thread_executor(self):
            if self._thread_executor is None:
                self._thread_executor = _ThreadPoolExecutor()

            return self._thread_executor

        @property
        def process_executor(self):
            if self._process_executor is None:
                self._process_executor = _ProcessPoolExecutor()

            return self._process_executor

        async def run_thread(
            self,
            function,
            /,
            *args,
            **kwargs,
        ):
            result = await _asyncio.to_thread(
                function,
                *args,
                **kwargs,
            )

            return result

        async def run_thread_pool(
            self,
            function,
            /,
            *args,
            **kwargs,
        ):
            loop = _asyncio.get_running_loop()

            result = await loop.run_in_executor(
                self.thread_executor,
                _partial(
                    function,
                    *args,
                    **kwargs,
                ),
            )

            return result

        async def run_process_pool(
            self,
            function,
            /,
            *args,
            **kwargs,
        ):
            loop = _asyncio.get_running_loop()

            result = await loop.run_in_executor(
                self.process_executor,
                _partial(
                    function,
                    *args,
                    **kwargs,
                ),
            )

            return result

        async def gather(
            self,
            *coroutines,
            return_exceptions=False,
        ):
            result = await _asyncio.gather(
                *coroutines,
                return_exceptions=return_exceptions,
            )

            return result

        async def wait(
            self,
            *coroutines,
            timeout=None,
        ):
            tasks = {
                _asyncio.create_task(coroutine)
                for coroutine in coroutines
            }

            result = await _asyncio.wait(
                tasks,
                timeout=timeout,
            )

            return result

        def create_task(
            self,
            coroutine,
            name=None,
        ):
            result = _asyncio.create_task(
                coroutine,
                name=name,
            )

            return result

        async def timeout(
            self,
            coroutine,
            seconds,
        ):
            result = await _asyncio.wait_for(
                coroutine,
                timeout=seconds,
            )

            return result

        async def map_thread(
            self,
            function,
            *iterables,
        ):
            result = await _asyncio.gather(
                *(
                    self.run_thread(
                        function,
                        *values,
                    )
                    for values in zip(
                        *iterables,
                        strict=True,
                    )
                )
            )

            return result

        async def map_thread_pool(
            self,
            function,
            *iterables,
        ):
            result = await _asyncio.gather(
                *(
                    self.run_thread_pool(
                        function,
                        *values,
                    )
                    for values in zip(
                        *iterables,
                        strict=True,
                    )
                )
            )

            return result

        async def map_process_pool(
            self,
            function,
            *iterables,
        ):
            result = await _asyncio.gather(
                *(
                    self.run_process_pool(
                        function,
                        *values,
                    )
                    for values in zip(
                        *iterables,
                        strict=True,
                    )
                )
            )

            return result

        def create_thread(
            self,
            function,
            /,
            *args,
            daemon=False,
            start=True,
            **kwargs,
        ):
            thread = _threading.Thread(
                target=function,
                args=args,
                kwargs=kwargs,
                daemon=daemon,
            )

            if start:
                thread.start()

            return thread

        def shutdown(
            self,
            *,
            wait=True,
        ):
            if self._thread_executor is not None:
                self._thread_executor.shutdown(
                    wait=wait,
                )

                self._thread_executor = None

            if self._process_executor is not None:
                self._process_executor.shutdown(
                    wait=wait,
                )

                self._process_executor = None

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            self.shutdown()

    _AsynchronousManager = __AsynchronousManager
    _allocate_module = lambda: None


def AsynchronousManager():
    if _AsynchronousManager is None:
        _allocate_module()

    return _AsynchronousManager


# AsynchronousManager()
