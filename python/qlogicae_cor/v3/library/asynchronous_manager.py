__all__ = (
    "AsynchronousManager",
)

_asyncio = None
_threading = None
_functools = None
_concurrent_futures = None
_AsynchronousManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _AsynchronousManager

    class __AsynchronousManager:
        __slots__ = (
            "_thread_executor",
            "_process_executor",
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
        def thread_executor(self):
            if self._thread_executor is None:
                self._thread_executor = _concurrent_futures().ThreadPoolExecutor()

            return self._thread_executor

        @property
        def process_executor(self):
            if self._process_executor is None:
                self._process_executor = _concurrent_futures().ProcessPoolExecutor()

            return self._process_executor

        def construct(self):
            global _ExternalDependencyManager
            global _asyncio
            global _threading
            global _functools
            global _concurrent_futures

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _asyncio = (
                _ExternalDependencyManager().import_module(
                    path="asyncio",
                )
            )
            _threading = (
                _ExternalDependencyManager().import_module(
                    path="threading",
                )
            )
            _functools = (
                _ExternalDependencyManager().import_module(
                    path="functools",
                )
            )
            _concurrent_futures = (
                _ExternalDependencyManager().import_module(
                    path="concurrent.futures",
                )
            )

            self._thread_executor = None
            self._process_executor = None

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

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

            return True

        async def run_thread(
            self,
            function,
            /,
            *args,
            **kwargs,
        ):
            result = await _asyncio().to_thread(
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
            loop = _asyncio().get_running_loop()

            result = await loop.run_in_executor(
                self.thread_executor,
                _functools().partial(
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
            loop = _asyncio().get_running_loop()

            result = await loop.run_in_executor(
                self.process_executor,
                _functools().partial(
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
            result = await _asyncio().gather(
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
                _asyncio().create_task(coroutine)
                for coroutine in coroutines
            }

            result = await _asyncio().wait(
                tasks,
                timeout=timeout,
            )

            return result

        def create_task(
            self,
            coroutine,
            name=None,
        ):
            result = _asyncio().create_task(
                coroutine,
                name=name,
            )

            return result

        async def timeout(
            self,
            coroutine,
            seconds,
        ):
            result = await _asyncio().wait_for(
                coroutine,
                timeout=seconds,
            )

            return result

        async def map_thread(
            self,
            function,
            *iterables,
        ):
            result = await _asyncio().gather(
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
            result = await _asyncio().gather(
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
            result = await _asyncio().gather(
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
            thread = _threading().Thread(
                target=function,
                args=args,
                kwargs=kwargs,
                daemon=daemon,
            )

            if start:
                thread.start()

            return thread


    _AsynchronousManager = __AsynchronousManager
    _allocate = lambda: None


def AsynchronousManager():
    if _AsynchronousManager is None:
        _allocate()

    return _AsynchronousManager


# AsynchronousManager()

