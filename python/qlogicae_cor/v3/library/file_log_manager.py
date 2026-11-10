__all__ = (
    "FileLogManager",
)

_logging = None
_queue = None
_logging_handlers = None
_pathlib = None
_TextEncodingManager = None
_LogFormat = None
_LogOptions = None
_LogOptionsManager = None
_FileLogManager = None
_ExternalDependencyManager = None


def _allocate():
    global _allocate
    global _FileLogManager

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
                    with _pathlib().Path.open(
                        current_file_path,
                        "a",
                        encoding=_TextEncodingManager().selected_encoding,
                    ) as file:
                        file.write(
                            f"{str(message).strip()}\n"
                        )

            return message

        def construct(self):
            global _ExternalDependencyManager
            global _logging
            global _queue
            global _logging_handlers
            global _pathlib
            global _TextEncodingManager
            global _LogFormat
            global _LogOptions
            global _LogOptionsManager

            from .external_dependency_manager import ExternalDependencyManager

            _ExternalDependencyManager = (
                ExternalDependencyManager().get_singleton
            )

            _logging = (
                _ExternalDependencyManager().import_module(
                    path="logging",
                )
            )
            _queue = (
                _ExternalDependencyManager().import_module(
                    path="queue",
                )
            )
            _logging_handlers = (
                _ExternalDependencyManager().import_module(
                    path="logging.handlers",
                )
            )
            _pathlib = (
                _ExternalDependencyManager().import_module(
                    path="pathlib",
                )
            )
            _TextEncodingManager = (
                _ExternalDependencyManager().import_module(
                    path=".text_encoding_manager",
                    package="qlogicae_cor.v3.library",
                    member="TextEncodingManager",
                    is_member_callable=True,
                )
            )
            _LogFormat = (
                _ExternalDependencyManager().import_module(
                    path=".log_format",
                    package="qlogicae_cor.v3.library",
                    member="LogFormat",
                    is_member_callable=True,
                )
            )
            _LogOptions = (
                _ExternalDependencyManager().import_module(
                    path=".log_options",
                    package="qlogicae_cor.v3.library",
                    member="LogOptions",
                    is_member_callable=True,
                )
            )
            _LogOptionsManager = (
                _ExternalDependencyManager().import_module(
                    path=".log_options_manager",
                    package="qlogicae_cor.v3.library",
                    member="LogOptionsManager",
                    is_member_callable=True,
                )
            )

            self.logger = _logging().getLogger("file-logger")
            self.logger.setLevel(_logging().DEBUG)
            self.logger.propagate = False
            self.logger.handlers.clear()

            self.file_handlers = {}

            self.log_queue = _queue().Queue()

            self.queue_handler = _logging_handlers().QueueHandler(
                self.log_queue,
            )

            self.logger.addHandler(
                self.queue_handler,
            )

            self.listener = _logging_handlers().QueueListener(
                self.log_queue,
            )

            self.listener.start()

            self._options = _LogOptions()()
            self._cache = []

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, (dict)) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            self._options = (
                kwargs.get(
                    "options",
                    _LogOptions()()
                ) or _LogOptions()()
            )

            target_filesystem_paths = (
                self._options.target_filesystem_paths or tuple()
            )
            for target_filesystem_path in target_filesystem_paths:
                if not target_filesystem_path:
                    continue

                self.add_file_output(
                    target_filesystem_path
                )

            return True

        def shutdown(self):
            self.log_cached()

            self.listener.stop()

            for handler in self.file_handlers.values():
                handler.close()

            self.file_handlers.clear()

            return True

        def cache_log(self, message, log_level):
            self._cache.append(
                (
                    message,
                    _LogOptionsManager().get_singleton().generate_modified_defaults(
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

        def log_debug(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    self._options,
                    log_level=_logging().DEBUG,
                ),
            )

        def log_info(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    self._options,
                    log_level=_logging().INFO,
                ),
            )

        def log_warning(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    self._options,
                    log_level=_logging().WARNING,
                ),
            )

        def log_error(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    self._options,
                    log_level=_logging().ERROR,
                ),
            )

        def log_critical(self, message):
            return self.log(
                message,
                _LogOptionsManager().get_singleton().generate_modified_defaults(
                    self._options,
                    log_level=_logging().CRITICAL,
                ),
            )

        def rebuild_listener(self):
            self.listener.stop()

            self.listener = _logging_handlers().QueueListener(
                self.log_queue,
                *self.file_handlers.values(),
            )

            self.listener.start()

            return True

        def add_file_output(self, file_path):
            path = _pathlib().Path(file_path).resolve()

            if path in self.file_handlers:
                return False

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            handler = _logging().FileHandler(
                path,
                encoding=_TextEncodingManager().get_singleton().selected_encoding,
            )

            handler.setFormatter(
                _LogFormat()(),
            )

            self.file_handlers[path] = handler
            self.rebuild_listener()

            return True

        def remove_file_output(self, file_path):
            path = _pathlib().Path(file_path).resolve()

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


    _FileLogManager = __FileLogManager
    _allocate = lambda: None


def FileLogManager():
    if _FileLogManager is None:
        _allocate()

    return _FileLogManager


# FileLogManager()
