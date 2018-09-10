import functools
import glob
import importlib
import os
import shlex
import re
import traceback
import time
from collections import namedtuple
from pprint import pprint
from typing import List, Type, Dict, Any

from command_line import SimpleCommand, ComplexCommand, Mode, command

from api.data_structures import SimpleStack
from api.paths import COMMANDS_DIR


Command_Entry = namedtuple("Command", ("run", "short_help", "help"))


class ModeStack(SimpleStack):
    def __init__(self, *args, **kwargs):
        super(ModeStack, self).__init__(*args, **kwargs)

    def iter(self):
        for mode in self._data:
            yield mode.display()

    def has_mode(self, mode_class: Type[Mode]):
        return self.get_mode(mode_class) is not None

    def get_mode(self, mode_class: Type[Mode]):
        if not isinstance(mode_class, type):
            raise TypeError("You must pass a Type")

        for mode in self._data:
            if isinstance(mode, mode_class):
                return mode

        return None


class CommandLineHandler:

    _reserved_commands = ("help", "exit")
    _command_regex = re.compile(r"^[a-zA-Z_]+\d*$")

    def in_mode(self, mode_class: Type[Mode]) -> bool:
        pass

    def get_mode(self, mode_class: Type[Mode]) -> Mode:
        pass

    def __init__(self):

        self.shared_data = {}

        self._commands = {}
        self._complex_commands = {}
        self._modes = ModeStack()

        self._retry_modules = []
        self._modules = []
        self._load_external = None
        self._load_commands_and_modes()

        self.in_mode = self._modes.has_mode
        self.get_mode = self._modes.get_mode

    def enter_mode(self, mode: Mode):
        """
        Enters the supplied Mode, but doesn't add it to the ModeStack unless enter() returns True

        :param mode: An instance of Mode to enter
        """
        if mode.enter():
            self._modes.append(mode)
        else:
            print(f"=== Error: Could not enter mode: {mode.__class__.__name__}")

    def exit_mode(self, force: bool = False) -> bool:
        """
        Exits the most current Mode if the Mode's exit() returns True. If False is returned, the user is
        notified. If ``force`` is True, then the return value of exit() is ignored.

        :param force: True if the return value of exit() is to be ignored
        :return: True if the Mode was successfully exited, False otherwise
        """
        if self._modes.is_empty():
            return False

        mode = self._modes.peek()
        result = mode.exit()
        if force:
            self._modes.pop()
        elif not result:
            print(f"======= Could not exit {mode.display()} ======")
            return False

        else:
            self._modes.pop()
        return True

    def _execute_command(self, command_parts):
        try:
            self._commands[command_parts[0]].run(command_parts)
        except Exception as e:
            cmd = " ".join(command_parts)
            print("==== Begin Exception Stacktrace ====")
            time.sleep(0.01)
            traceback.print_exc()
            time.sleep(0.01)
            print("==== End Exception Stacktrace ====")
            print(
                f"=== Error: An Exception has occurred while running command: '{cmd}'"
            )

    def _exit(self, force=False) -> bool:
        while not self._modes.is_empty():
            result = self.exit_mode(force)
            if not result:
                print(f"======= Could not exit {mode.display()} ======")
                return False

        return True

    def run(self):
        while True:
            user_input = input(f"{' | '.join(self._modes.iter())}> ")

            if not user_input:
                continue

            if user_input.count('"') % 2 != 0 or user_input.count("'") % 2 != 0:
                print(
                    "=== Error: You do not have an even amount of quotations in your entered command, please re-enter your command"
                )
                continue

            command_parts = shlex.split(user_input)

            if command_parts[0] == "exit":
                if not self._exit("-f" in command_parts):
                    continue

                break

            if command_parts[0] == PopModeCommand.command:
                self._commands[command_parts[0]].run(command_parts)

            if command_parts[0].startswith("$"):
                self._commands["$"].run(command_parts)
                continue

            if command_parts[0] == "help":
                if len(command_parts) > 1:
                    if command_parts[1] in self._commands:
                        print(f"==== {command_parts[1].capitalize()} Command Help ====")
                        self._commands[command_parts[1]].help()
                    elif command_parts[1] in self._complex_commands:
                        print(f"==== {command_parts[1].capitalize()} Command Help ====")
                        self._complex_commands[command_parts[1]].help()
                    else:
                        print(f'help: Command "{command_parts[1]}" not recognized')
                        continue

                else:
                    print("============= Registered Commands =============")
                    print("help - Displays all registered commands and their summaries")
                    print("exit - Exits the command line interface")
                    for cmd, inst in self._commands.items():
                        if "." in cmd:
                            continue

                        print(f"{cmd} - {inst.short_help():.51}")

                    for ccmd, inst in self._complex_commands.items():
                        print(f"{ccmd} - {inst.short_help():.51}")

            if command_parts[0] in self._complex_commands:
                if "-h" in command_parts:
                    print(f"==== {command_parts[0].capitalize()} Command Help ====")
                    self._complex_commands[command_parts[0]].help()
                    continue
                else:
                    if "." not in command_parts[0]:
                        if command_parts[0] in self._complex_commands:
                            print(
                                f'"{command_parts[0]}" is not a valid command, try "{command_parts[0]} -h"'
                            )
                            continue

                        print(f'Command "{command_parts[0]}" is not recognized')
                        continue

                    new_command_parts = [f"{command_parts[0]}.{command_parts[1]}"]
                    new_command_parts.extend(command_parts[2:])
                    command_parts = new_command_parts

            if command_parts[0] in self._commands:
                if "-h" in command_parts:
                    print(f"==== {command_parts[0].capitalize()} Command Help ====")
                    self._commands[command_parts[0]].help()
                else:
                    if self._modes.is_empty():
                        self._execute_command(command_parts)
                    else:
                        result = self._modes.peek().before_execution(command_parts)
                        if result is None or result:
                            self._execute_command(command_parts)
            else:
                print(f'Command "{command_parts[0]}" is not recognized')

        return 0

    def _load_commands_and_modes(self, reload=False):

        if reload:
            self._commands = {}
            self._complex_commands = {}
            self._retry_modules = []
            self._modules = []

        builtin_search_path = os.path.join(
            os.path.dirname(COMMANDS_DIR), "builtin_commands"
        )
        search_path = os.path.join(os.path.dirname(COMMANDS_DIR), "commands")

        cmds = [
            cmd
            for cmd in glob.iglob(
                os.path.join(builtin_search_path, "**", "*.py"), recursive=True
            )
            if not cmd.endswith("__init__.py")
        ]
        other_cmds = [
            cmd
            for cmd in glob.iglob(
                os.path.join(search_path, "**", "*.py"), recursive=True
            )
            if not cmd.endswith("__init__.py")
        ]
        if other_cmds:
            if self._load_external is None:
                print("Detected loadable 3rd party command-line modules. These modules")
                print(
                    "cannot be verified to be stable and/or contain malicious code. If"
                )
                print("you enable these modules, you use them at your own risk")
                answer = input("Would you like to enable them anyway? (y/n)> ")
                self._load_external = answer == "y"
            else:
                answer = "y" if self._load_external else "n"

            if answer.lower() == "y":
                cmds.extend(other_cmds)

        for cmd in cmds:
            try:
                module = importlib.import_module(
                    cmd[cmd.find("command_line") :].replace(os.path.sep, ".")[:-3]
                )
                self._modules.append(module)
            except ImportError:
                self._retry_modules.append(os.path.basename(cmd)[:-3])

        for mod in self._retry_modules:
            try:
                module = importlib.import_module(mod)
                self._modules.append(module)
            except ImportError as e:
                print(f"Couldn't import {mod} due to error: {e}")

        del self._retry_modules

        simple_commands = SimpleCommand.get_subclasses()
        for cmd in simple_commands:

            if not getattr(cmd, "registered", False):
                continue

            command_func, command_name = cmd.command

            if not self._command_regex.match(command_name) and command_name != "$":
                print(
                    f"Could not enable command {command_name} since it doesn't have a valid command name/prefix"
                )
                continue

            if command_name in self._reserved_commands:
                print(
                    f"Could not enable command {command_name} since another command uses the same prefix!"
                )

            command_instance = cmd(self)
            self._commands[command_name] = Command_Entry(
                functools.partial(command_func, command_instance),
                command_instance.short_help,
                command_instance.help,
            )

        complex_commands = ComplexCommand.get_subclasses()
        for cmd in complex_commands:

            if not getattr(cmd, "registered", False):
                continue

            base_command = cmd.base_command
            command_instance = cmd(self)

            self._complex_commands[base_command] = command_instance

            for command_name, func in cmd.sub_commands.items():
                self._commands[f"{base_command}.{command_name}"] = Command_Entry(
                    functools.partial(func, command_instance),
                    command_instance.short_help,
                    functools.partial(command_instance.help, command_name),
                )


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
