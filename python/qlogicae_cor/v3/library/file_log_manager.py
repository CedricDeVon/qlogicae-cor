__all__ = (
    "FileLogManager",
)

_logging = None
_queue = None
_QueueHandler = None
_QueueListener = None
_Path = None
_PythonRuntimeUtilityManager = None
_TextEncodingManager = None
_LogFormat = None
_LogOptions = None
_LogOptionsManager = None
_FileLogManager = None


def _allocate_module():
    global _allocate_module
    global _logging
    global _queue
    global _QueueHandler
    global _QueueListener
    global _Path
    global _PythonRuntimeUtilityManager
    global _TextEncodingManager
    global _LogFormat
    global _LogOptions
    global _LogOptionsManager
    global _FileLogManager

    import logging
    import queue
    from logging.handlers import QueueHandler, QueueListener
    from pathlib import Path

    from .log_format import LogFormat
    from .log_options import LogOptions
    from .log_options_manager import LogOptionsManager
    from .python_runtime_utility_manager import PythonRuntimeUtilityManager
    from .text_encoding_manager import TextEncodingManager

    _logging = logging
    _queue = queue
    _QueueHandler = QueueHandler
    _QueueListener = QueueListener
    _Path = Path
    _PythonRuntimeUtilityManager = PythonRuntimeUtilityManager()
    _TextEncodingManager = TextEncodingManager().get_singleton
    _LogFormat = LogFormat()
    _LogOptions = LogOptions()
    _LogOptionsManager = LogOptionsManager().get_singleton

    class __FileLogManager:
        __slots__ = (
            "logger",
            "file_handlers",
            "log_queue",
            "queue_handler",
            "listener",
            "_options",
            "_cache",
        )

        _singleton = None

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def __init__(self):
            if _PythonRuntimeUtilityManager.is_allocated_during_object_construction:
                _LogOptionsManager()
                _TextEncodingManager()

            self.logger = _logging.getLogger("file-logger")
            self.logger.setLevel(_logging.DEBUG)
            self.logger.propagate = False
            self.logger.handlers.clear()

            self.file_handlers = {}

            self.log_queue = _queue.Queue()

            self.queue_handler = _QueueHandler(
                self.log_queue,
            )

            self.logger.addHandler(
                self.queue_handler,
            )

            self.listener = _QueueListener(
                self.log_queue,
            )

            self.listener.start()

            self._options = _LogOptions()
            self._cache = []

        def cache_log(self, message, log_level):
            self._cache.append(
                (
                    message,
                    _LogOptionsManager().generate_modified_defaults(
                        self._options,
                        log_level=log_level,
                    ),
                )
            )

            return message

        def log_cached(self):
            for message, options in self._cache:
                self.log(
                    message,
                    options,
                )

            self._cache.clear()

            return True

        @property
        def options(self):
            return self._options

        @options.setter
        def options(self, value):
            self._options = value

        def log(self, message, options):
            if not options.is_enabled:
                return message

            if options.is_verbose_enabled:
                self.logger.log(
                    options.log_level,
                    str(message).strip(),
                    stacklevel=options.stack_level,
                )
            else:
                for current_file_path in self.file_handlers:
                    with _Path.open(
                        current_file_path,
                        "a",
                        encoding=_TextEncodingManager().selected_encoding,
                    ) as file:
                        file.write(
                            f"{str(message).strip()}\n"
                        )

            return message

        def log_debug(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.DEBUG,
                ),
            )

        def log_info(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.INFO,
                ),
            )

        def log_warning(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.WARNING,
                ),
            )

        def log_error(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.ERROR,
                ),
            )

        def log_critical(self, message):
            return self.log(
                message,
                _LogOptionsManager().generate_modified_defaults(
                    self._options,
                    log_level=_logging.CRITICAL,
                ),
            )

        def rebuild_listener(self):
            self.listener.stop()

            self.listener = _QueueListener(
                self.log_queue,
                *self.file_handlers.values(),
            )

            self.listener.start()

            return True

        def add_file_output(self, file_path):
            path = _Path(file_path).resolve()

            if path in self.file_handlers:
                return False

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            handler = _logging.FileHandler(
                path,
                encoding=_TextEncodingManager().selected_encoding,
            )

            handler.setFormatter(
                _LogFormat(),
            )

            self.file_handlers[path] = handler
            self.rebuild_listener()

            return True

        def remove_file_output(self, file_path):
            path = _Path(file_path).resolve()

            handler = self.file_handlers.get(path)

            if handler is None:
                return False

            handler.close()

            del self.file_handlers[path]

            self.rebuild_listener()

            return True

        def clear_file_outputs(self):
            for handler in self.file_handlers.values():
                handler.close()

            self.file_handlers.clear()

            self.rebuild_listener()

            self._cache.clear()

            return True

        def shutdown(self):
            self.log_cached()

            self.listener.stop()

            for handler in self.file_handlers.values():
                handler.close()

            self.file_handlers.clear()

            return True

    _FileLogManager = __FileLogManager
    _allocate_module = lambda: None


def FileLogManager():
    if _FileLogManager is None:
        _allocate_module()

    return _FileLogManager


# FileLogManager()
