__all__ = (
    "ExternalDependencyManager",
)

_importlib = None
_ImportTarget = None
_ExternalDependencyManager = None

def _allocate():
    global _allocate
    global _ImportTarget
    global _ExternalDependencyManager

    class __ImportTarget:
        __slots__ = (
            "_name",
            "_path",
            "_package",
            "_allocated_module",
            "_is_pre_allocated",
            "_is_member_callable",
            "_member",
        )

        def __init__(self, **kwargs):
            self.construct(**kwargs)

        def __enter__(self):
            self.allocate()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @property
        def name(self):
            return self._name

        @name.setter
        def name(self, value):
            if not value or not isinstance(value, str):
                raise ValueError("'name' must be a non-empty string")

            self._name = value

        @property
        def path(self):
            return self._path

        @path.setter
        def path(self, value):
            if not value or not isinstance(value, str):
                raise ValueError("'path' must be a non-empty string")

            self._path = value

        @property
        def is_member_callable(self):
            return self._is_member_callable

        @is_member_callable.setter
        def is_member_callable(self, value):
            if not isinstance(value, (bool)):
                raise ValueError("'is_member_callable' must be a boolean")

            self._is_member_callable = value

        @property
        def package(self):
            return self._package

        @package.setter
        def package(self, value):
            if value is not None and not isinstance(value, str):
                raise TypeError("'package' must be a string or None")


            self._package = value or None

        @property
        def member(self):
            return self._member

        @member.setter
        def member(self, value):
            if value is not None and not isinstance(value, str):
                raise TypeError("'member' must be a string or None")


            self._member = value or None

        @property
        def allocated_module(self):
            return self._allocated_module

        @allocated_module.setter
        def allocated_module(self, value):
            self._allocated_module = value

        @property
        def is_pre_allocated(self):
            return self._is_pre_allocated

        @is_pre_allocated.setter
        def is_pre_allocated(self, value):
            if not isinstance(value, (bool)):
                raise TypeError("'is_pre_allocated' must be a boolean")

            self._is_pre_allocated = value

        def construct(self, **kwargs):
            if not isinstance(kwargs, dict) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            path = kwargs.get("path")

            if not isinstance(path, str) or not path:
                raise ValueError("'kwargs.path' must be a non-empty string")

            self._path = path

            name = kwargs.get("name")

            if name is not None and not isinstance(name, str):
                raise ValueError("'kwargs.name' must be a string")

            self._name = name or path

            package = kwargs.get("package")

            if package is not None and not isinstance(package, str):
                raise TypeError("'kwargs.package' must be a string or None")

            self._package = package or None

            is_pre_allocated = kwargs.get("is_pre_allocated", False)

            if not isinstance(is_pre_allocated, bool):
                raise ValueError("'kwargs.is_pre_allocated' must be a boolean")

            member = kwargs.get("member", "")

            if member is not None and not isinstance(member, str):
                raise TypeError("'kwargs.member' must be a string or None")

            self._member = member

            is_member_callable = kwargs.get("is_member_callable", False)

            if not isinstance(is_member_callable, bool):
                raise ValueError("'kwargs.is_member_callable' must be a boolean")

            self._is_member_callable = (
                is_member_callable
            )
            self._is_pre_allocated = is_pre_allocated
            self._allocated_module = None

            if self._is_pre_allocated:
                self.allocate()

            return True

        def shutdown(self):
            self.deallocate()
            return True

        def setup(self, **kwargs):
            if not kwargs or not isinstance(kwargs, (dict)):
                raise ValueError("'kwargs' must be a non-empty dictionary")

            return True

        def allocate(self):
            if self._allocated_module:
                return self._allocated_module

            if self._package:
                allocated_module = _importlib.import_module(
                    self._path,
                    package=self._package,
                )
            else:
                allocated_module = _importlib.import_module(
                    self._path,
                )

            if self._member:
                for name in self._member.split("."):
                    if not name:
                        continue

                    allocated_module = getattr(
                        allocated_module,
                        name,
                    )

            if self._is_member_callable:
                self._allocated_module = allocated_module()

            else:
                self._allocated_module = allocated_module

            return self._allocated_module

        def pre_allocate(self):
            if not self._allocated_module:
                self.allocate()

            return self._allocated_module

        def deallocate(self):
            if not self._allocated_module:
                return self._allocated_module

            self._allocated_module = (
                None
            )

            return self._allocated_module

        def reallocate(self):
            if self._allocated_module:
                self.deallocate()

            self.allocate()

            return self._allocated_module


    class __ExternalDependencyManager:
        __slots__ = (
            "_import_targets",
            "_is_pre_allocated"
        )

        _singleton = None

        def __init__(self):
            self.construct()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.shutdown()

        @property
        def is_pre_allocated(self):
            return self._is_pre_allocated

        @is_pre_allocated.setter
        def is_pre_allocated(self, value):
            if not isinstance(value, bool):
                raise TypeError("'value' must be a boolean")

            self._is_pre_allocated = value

        @property
        def import_targets(self):
            return self._import_targets

        @import_targets.setter
        def import_targets(self, value):
            if not isinstance(value, dict) or not value:
                raise ValueError(
                    "'import_targets' must be a non-empty dictionary"
                )

            for name, target in value.items():
                if not isinstance(name, str) or not name:
                    raise ValueError(
                        "'import_targets' keys must be non-empty strings"
                    )

                if not isinstance(target, _ImportTarget):
                    raise ValueError(
                        "'import_targets' values must be ImportTarget instances"
                    )

            self._import_targets = value

        @classmethod
        def get_singleton(cls):
            if cls._singleton is None:
                cls._singleton = cls()

            return cls._singleton

        def construct(self):
            global _importlib

            import importlib

            _importlib = (
                importlib
            )

            self._import_targets = {}
            self._is_pre_allocated = False

            return True

        def setup(self, **kwargs):
            if not isinstance(kwargs, dict) or not kwargs:
                raise ValueError("'kwargs' must be a non-empty dictionary")

            import_targets = kwargs.get("import_targets", ())

            if not isinstance(import_targets, (tuple, list)):
                raise ValueError(
                    "'kwargs.import_targets' must be a tuple or list"
                )

            is_pre_allocated = kwargs.get(
                "is_pre_allocated",
                self._is_pre_allocated,
            )

            if not isinstance(is_pre_allocated, bool):
                raise ValueError(
                    "'kwargs.is_pre_allocated' must be a boolean"
                )

            staged_targets = {}

            for target in import_targets:
                if not isinstance(target, dict) or not target:
                    raise ValueError(
                        "'import_targets[]' must contain non-empty dictionaries"
                    )

            try:
                for target_kwargs in import_targets:
                    target_kwargs = dict(target_kwargs)
                    target_kwargs["is_pre_allocated"] = is_pre_allocated

                    target = _ImportTarget(**target_kwargs)

                    if target.name not in self._import_targets:
                        staged_targets.setdefault(target.name, target)
                    else:
                        target.deallocate()

            except Exception:
                for target in staged_targets.values():
                    target.deallocate()

                raise

            self._import_targets.update(staged_targets)
            self._is_pre_allocated = is_pre_allocated

            return True

        def shutdown(self):
            self.clear_modules()
            return True

        def import_modules(
            self,
            targets
        ):
            if not isinstance(targets, (tuple, list)):
                raise ValueError("'targets' must be a tuple or list")

            for target in targets:
                if not target or not isinstance(target, (dict)):
                    raise ValueError("'targets[]' must contain non-empty dictionaries")

                self.import_module(
                    **target
                )

            return True

        def import_module(
            self,
            **kwargs,
        ):
            if not kwargs or not isinstance(kwargs, (dict)):
                raise ValueError("'kwargs' must be a non-empty dictionary")

            target_key = (
                (kwargs.get("name", "") or "")
                if "name" in kwargs
                else (kwargs.get("path", "") or "")
            )
            if not isinstance(target_key, (str)):
                raise ValueError("'kwargs.name' or 'kwargs.path' must be a string")

            import_target = None
            if target_key not in self._import_targets:
                kwargs["is_pre_allocated"] = (
                    self._is_pre_allocated
                )

                import_target = _ImportTarget(
                    **kwargs
                )
                if not import_target:
                    raise ValueError("'import_target' must be defined")

                self._import_targets[target_key] = (
                    import_target
                )

            else:
                import_target = (
                    self._import_targets[target_key]
                )

            import_target_allocate = (
                getattr(
                    import_target,
                    "allocate",
                    None
                ) or None
            )

            return (
                import_target_allocate
            )

        def pre_load_modules(self):
            for _key, import_target in self._import_targets.items():
                import_target.pre_allocate()

            return True

        def unload_modules(
            self,
            names,
        ):
            if not isinstance(names, (tuple, list)):
                raise ValueError("'names' must be a tuple or list")

            for name in names:
                if not name or not isinstance(name, (str)):
                    raise ValueError("'name' must be a non-empty string")

                self.unload_module(
                    name
                )

            return True

        def unload_module(
            self,
            name,
        ):
            if not name or not isinstance(name, (str)):
                raise ValueError("'name' must be a non-empty string")

            if name not in self._import_targets:
                raise ValueError(f"'{name}' must be a collection item")

            self._import_targets[name].deallocate()

            del self._import_targets[name]

            return True

        def clear_modules(
            self,
        ):
            if not len(self._import_targets):
                return True

            self.unload_modules(
                tuple(self._import_targets.keys())
            )

            return True


    _ImportTarget = __ImportTarget
    _ExternalDependencyManager = __ExternalDependencyManager
    _allocate = lambda: None


def ExternalDependencyManager():
    if _ExternalDependencyManager is None:
        _allocate()

    return _ExternalDependencyManager



# def ExternalDependencyManager():
#     if _ImportTarget is None:
#         _allocate()

#     return _ImportTarget

# ExternalDependencyManager()

# ExternalDependencyManager().get_singleton().setup(
#     import_targets=(
#         {"path": "importlib"},
#         {"path": "datetime"},
#         {"path": "os"},
#         {"path": "platform"},
#         {"path": "shlex"},
#         {"path": "subprocess"},
#         {"path": "importlib.util"},
#         {"path": "pickle"},
#         {"path": "time"},
#         {"path": "dbm.gnu"},
#         {"path": "copy"},
#         {"path": "re"},
#         {"path": "collections.abc"},
#         {"path": "json"},
#         {"path": "typing"},
#         {"path": "shutil"},
#         {"path": "zipfile"},
#         {"path": "queue"},
#         {"path": "logging.handlers"},
#         {"path": "pathlib"},
#         {"path": "dataclasses"},
#         {"path": "enum"},
#         {"path": "logging"},
#         {"path": "argparse"},
#         {"path": "sys"},
#         {"path": "asyncio"},
#         {"path": "threading"},
#         {"name": "awa", "path": "concurrent.futures"},
#         {"path": "functools"},
#     ),
#     is_pre_allocated=True
# )
# print(
#     ExternalDependencyManager().get_singleton().is_pre_allocated
# )
# for target, value in (
#     ExternalDependencyManager().get_singleton().import_targets.items()
# ):
#     v = ExternalDependencyManager().get_singleton().import_module(
#         name=target
#     )
#     # print(f"{target} - {v}")
#     print(v())
