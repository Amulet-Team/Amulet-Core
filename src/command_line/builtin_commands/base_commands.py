import importlib
from typing import List, Dict, Any
from pprint import pprint

from command_line import SimpleCommand, command


class VariableCommand(SimpleCommand):
    registered = True

    def traverse_dict(self, keys: List[str], create=False) -> Dict[str, Any]:
        current_dict = self.handler.shared_data
        for key in keys:
            if not create and key not in current_dict:
                print(f"Couldn't find shared data object \"{':'.join(keys)}\"")
                return {}

            elif create:
                current_dict[key] = {}
            current_dict = current_dict[key]
        return current_dict

    def run(self, args: List[str]):
        if len(args) == 1 and args[0] == "$":
            pprint(self.handler.shared_data)
        elif len(args) == 1:
            entry = self.get_shared_data(args[0])

            if entry:
                print(f"{args[0][1:]}: {str(entry)}")
            else:
                print(f'Couldn\'t find shared data object "{args[0][1:]}"')
        elif len(args) == 2:
            depth = args[0][1:].split(":")
            current_dict = self.traverse_dict(depth[:-1])

            if args[1] == "-" and depth[-1] in current_dict:
                del current_dict[depth[-1]]
            elif depth[-1] not in current_dict:
                print(f'Key "{args[0][1:]}" doesn\'t exist')

        elif len(args) == 3:
            depth = args[0][1:].split(":")
            current_dict = self.traverse_dict(depth[:-1], create=True)

            if args[1] == "=":
                current_dict[depth[-1]] = args[2]

    def help(self):
        print(
            "Allows viewing and basic manipulation of shared data between commands and the command-line\n"
        )
        print("=== Viewing Data ===")
        print("Shows all saved data:")
        print("Usage: $\n")
        print(
            "Shows a subset of data, with each key of a dictionary being seperated by a ':'"
        )
        print("Usage: $base_key:another_key...\n\n")
        print("=== Manipulating Data ===")
        print(
            "Creating an entry is pretty straight forward, values are only stored as strings"
        )
        print(
            "Creating a nested key will automatically create the parent dictionaries if they don't exist\n"
        )
        print("To create a new entry:")
        print("Usage: $test_key = value")
        print("Usage: $base_key:test_key = value\n")
        print("To delete an entry:")
        print("Usage: $test_key -")

    def short_help(self):
        return "Allows access to shared variables"

    command = (run, "$")


@command("reload")
class ReloadCommand(SimpleCommand):

    def help(self):
        print("Running this command reloads all registered commands and modes")
        print("Usage: reload")

    def short_help(self) -> str:
        return "Reloads all registered commands and modes"

    def run(self, args: List[str]):
        modules = getattr(self.handler, "_modules", ())
        for mod in modules:
            importlib.reload(mod)
        func = getattr(self.handler, "_load_commands_and_modes")
        if func:
            func(reload=True)
        print("Successfully reloaded commands and modes")


@command("pop_mode")
class PopModeCommand(SimpleCommand):

    def run(self, args: List[str]):
        self.handler.exit_mode("-f" in args)

    def help(self):
        print("Exits the most current mode and returns execution")
        print("to the previous mode. If a mode is unable to be exited")
        print("the '-f' argument forcefully exits the mode\n")
        print("Usage: pop_mode <-f>")

    def short_help(self) -> str:
        return "Exits the most current mode"
