import glob
import importlib
import os
import sys
import re
from typing import List


class Command:

    @classmethod
    def get_subclasses(cls) -> List:
        result = []
        for subcls in cls.__subclasses__():
            result.append(subcls)
        return result

    def run(self, args: List[str]):
        raise NotImplementedError()

    def help(self):
        raise NotImplementedError()


class CommandLineHandler:

    reserved_commands = ("help", "exit")
    regex = re.compile(r"^[a-zA-Z]+\d*$")

    def __init__(self):

        self.commands = {}
        self.modes = []
        self.load_commands()

    def run(self):
        while True:
            user_input = input("> ")

            if not user_input:
                continue

            if user_input == "exit":
                break

            if user_input == "help":
                print("==== Registered Commands ====")
                for cmd in self.commands.keys():
                    print(cmd)

            command_parts = user_input.split(" ")

            if command_parts[0] in self.commands:
                if "-h" in command_parts:
                    self.commands[command_parts[0]].help()
                else:
                    self.commands[command_parts[0]].run(command_parts)
        return 0

    def load_commands(self):
        search_path = os.path.join(os.path.dirname(__file__), "commands")
        sys.path.insert(0, os.path.join(search_path))

        cmds = glob.glob(os.path.join(search_path, "*.py"))
        for cmd in cmds:
            module = importlib.import_module(os.path.basename(cmd)[:-3])
        commands = Command.get_subclasses()
        for command in commands:
            command_name = command.command

            if not (
                self.regex.match(command_name) or command_name in self.reserved_commands
            ):
                continue

            self.commands[command.command] = command()


def init():
    return CommandLineHandler()
