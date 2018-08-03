import glob
import importlib
import os
import shlex
import sys
import re
import traceback
import time
from typing import List, Type

from api.cmd_line import SimpleCommand, ComplexCommand, Mode
from api.data_structures import SimpleStack
from api.paths import COMMANDS_DIR


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
        """
        Stub method for checking whether the program is in the specified Mode

        :param mode_class: The class of the Mode to check for
        :return: True if the program is in the specified Mode, False otherwise
        """
        pass

    def get_mode(self, mode_class: Type[Mode]) -> Mode:
        """
        Stub method for getting a Mode that the program is in

        :param mode_class: The class of the Mode instance to get
        :return: The instance of the specified Mode, None if the mode hasn't been entered
        """
        pass

    def __init__(self):

        self._commands = {}
        self._complex_commands = {}
        self._modes = ModeStack()

        self._retry_modules = []
        self._modules = []
        self._load_commands_and_modes()

        self.persistent_data = {}

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
            print(f"=== Error: An Exception has occurred while running command: '{cmd}'")


    def _exit(self, force=False) -> bool:
        while not self._modes.is_empty():
            result = self.exit_mode(force)
            if not result:
                print(f"======= Could not exit {mode.display()} ======")
                return False

        return True

    def _run(self):
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
        return 0

    def _load_commands_and_modes(self):
        search_path = os.path.join(os.path.dirname(COMMANDS_DIR), "commands")
        sys.path.insert(0, os.path.join(search_path))

        cmds = glob.glob(os.path.join(search_path, "*.py"))
        if cmds:
            print("Detected loadable 3rd party command-line modules. These modules")
            print("cannot be verified to be stable and/or contain malicious code. If")
            print("you enable these modules, you use them at your own risk")
            answer = input("Would you like to enable them anyway? (y/n)> ")

            if answer.lower() == "y":
                for cmd in cmds:
                    try:
                        module = importlib.import_module(os.path.basename(cmd)[:-3])
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
        for command in simple_commands:
            command_name = command.command

            if not self._command_regex.match(command_name):
                print(
                    f"Could not enable command {command_name} since it doesn't have a valid command name/prefix"
                )
                continue

            if command_name in self._reserved_commands:
                print(
                    f"Could not enable command {command_name} since another command uses the same prefix!"
                )

            self._commands[command.command] = command(self)

        complex_commands = ComplexCommand.get_subclasses()
        for command in complex_commands:
            base_command = command.base
            children = command.get_children()

            self._complex_commands[base_command] = command

            for child in children:
                command_inst = self._commands.get(child.command)
                if not command_inst:
                    command_inst = child(self)
                else:
                    del self._commands[child.command]
                self._commands[f"{base_command}.{child.command}"] = command_inst


class ReloadCommand(SimpleCommand):

    command = "reload"

    def help(self):
        print("Running this command reloads all registered commands and modes")
        print("Usage: reload")

    def short_help(self) -> str:
        return "Reloads all registered commands and modes"

    def run(self, args: List[str]):
        # self.handler.load_commands_and_modes()
        modules = getattr(self.handler, "_modules", ())
        for mod in modules:
            importlib.reload(mod)
        print("Successfully reloaded commands and modes")


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

    command = "pop_mode"


def init():
    return CommandLineHandler()
