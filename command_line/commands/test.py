from typing import List

from command_line import SimpleCommand, Mode


class TestCommand(SimpleCommand):

    def short_help(self) -> str:
        return "Test Command"

    def run(self, args: List[str]):
        print("This is a test command that doesn't do anything!")

    def help(self):
        print("This command does nothing notable")

    command = "test"


class TestTestCommand(TestCommand):
    pass


class EchoCommand(SimpleCommand):

    def short_help(self) -> str:
        return "Echoes the entire command and arguments"

    def run(self, args: List[str]):
        print(f'Got the following command: {" ".join(args)}')

    def help(self):
        print("Echoes the supplied command and it's arguments back to the user")

    command = "echo"


class TestMode(Mode):
    pass


class TestTestMode(TestMode):
    pass
