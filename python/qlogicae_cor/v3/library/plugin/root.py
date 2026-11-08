__all__ = (
    "export"
)

def print_message(arguments):
    for target in arguments.target:
        print(target)



def on_pre_setup():
    print("exports _ on_pre_setup")


def on_post_setup():
    print("exports - on_post_setup")


def on_pre_run():
    print("exports - on_pre_run")


def on_post_run():
    print("exports - on_post_run")


def export():
    data = {
        "command": {
            "options": {
                "args": (),
                "kwargs": {
                    "prog": "name",
                    "description": "command description",
                    "add_help": True,
                    "allow_abbrev": False,
                },
                "commands": [
                    {
                        "name": "print",
                        "args": (),
                        "kwargs": {
                            "help": "print message",
                            "aliases": (),
                        },
                        "command_handler": print_message,
                        "arguments": [
                            {
                                "args": (
                                    "-t",
                                    "--target",
                                ),
                                "kwargs": {
                                    "help": "argument description",
                                    "dest": "target",
                                    "action": "append",
                                    "default": [],
                                    "type": str,
                                    "required": True,
                                    "nargs": "+",
                                    "metavar": "TARGET",
                                },
                            },
                        ],
                    },
                ],
                "subparsers": {
                    "args": (),
                    "kwargs": {
                        "dest": "command",
                        "required": True,
                        "title": "commands",
                        "description": None,
                        "metavar": "",
                    },
                },
            },
            "callbacks": {
                "on_pre_setup": on_pre_setup,
                "on_post_setup": on_post_setup,
            },
        },
        "database": {
            "is_enabled": True,
            "value_cache": {
                "is_enabled": True,
                "options": {
                    "values": {
                        "key": "",
                    },
                    "defaults": {
                        "key": "value",
                    }
                }
                "callbacks": {
                    "on_pre_setup": on_pre_setup,
                    "on_post_setup": on_post_setup,
                },
            },
            "persistent_cache": {
                "is_enabled": True,
                "options": {
                    "database_path": "data.db",
                },
                "callbacks": {
                    "on_pre_setup": on_pre_setup,
                    "on_post_setup": on_post_setup,
                },
            },
            "callbacks": {
                "on_pre_setup": on_pre_setup,
                "on_post_setup": on_post_setup,
            },
        },
        "log": {
            "is_enabled": True,
            "file": {
                "options": {
                    "is_enabled": True,
                    "is_verbose_enabled": True,
                    "log_level": 10,
                    "stack_level": 3,
                    "targets": [],
                },
                "callbacks": {
                    "on_pre_setup": on_pre_setup,
                    "on_post_setup": on_post_setup,
                },
            },
            "console": {
                "options": {
                    "is_enabled": True,
                    "is_verbose_enabled": True,
                    "log_level": 10,
                    "stack_level": 3,
                },
                "callbacks": {
                    "on_pre_setup": on_pre_setup,
                    "on_post_setup": on_post_setup,
                },
            },
            "callbacks": {
                "on_pre_setup": on_pre_setup,
                "on_post_setup": on_post_setup,
            },
        },
    }

    return data

