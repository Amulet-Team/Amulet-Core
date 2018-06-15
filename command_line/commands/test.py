from typing import List

from command_line import Command


class TestCommand(Command):

    def run(self, args: List[str]):
        print("This is a test command that doesn't do anything!")

    def help(self):
        print("This command does nothing notable")

    command = "test"


class EchoCommand(Command):

    def run(self, args: List[str]):
        print('Got the following command: "{}"'.format(" ".join(args)))

    def help(self):
        print("Echoes the supplied command and it's arguments back to the user")

    command = "echo"
