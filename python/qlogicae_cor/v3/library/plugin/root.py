# __all__ = (
#     "export"
# )

# def print_message(arguments):
#     for target in arguments.target:
#         print(target)


# def export():
#     data = {
#         "cli": {
#             "args": (),
#             "kwargs": {
#                 "prog": "name",
#                 "description": "command description",
#                 "add_help": True,
#                 "allow_abbrev": False,
#             },
#             "commands": [
#                 {
#                     "name": "print",
#                     "args": (),
#                     "kwargs": {
#                         "help": "print message",
#                         "aliases": (),
#                     },
#                     "command_handler": print_message,
#                     "arguments": [
#                         {
#                             "args": (
#                                 "-t",
#                                 "--target",
#                             ),
#                             "kwargs": {
#                                 "help": "argument description",
#                                 "dest": "target",
#                                 "action": "append",
#                                 "default": [],
#                                 "type": str,
#                                 "required": True,
#                                 "nargs": "+",
#                                 "metavar": "TARGET",
#                             },
#                         },
#                     ],
#                 },
#             ],
#             "subparsers": {
#                 "args": (),
#                 "kwargs": {
#                     "dest": "command",
#                     "required": True,
#                     "title": "commands",
#                     "description": None,
#                     "metavar": "",
#                 },
#             },
#         }
#     }

#     return data

