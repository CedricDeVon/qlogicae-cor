__all__ = (
    "export"
)

def print_message(arguments):
    for target in arguments.target:
        for a in target:
            print(a)



def on_pre_setup():
    print("exports - on_pre_setup")


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
            },
            "callbacks": {
                "on_pre_setup": on_pre_setup,
                "on_post_setup": on_post_setup,
                "on_pre_run": on_pre_run,
                "on_post_run": on_post_run,
            },
        },
    }

    return data

