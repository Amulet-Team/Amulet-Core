from typing import List

from command_line import SimpleCommand, Mode, command


@command("test")
class TestCommand(SimpleCommand):

    def short_help(self) -> str:
        return "Test Command"

    def run(self, args: List[str]):
        print("This is a test command that doesn't do anything!")

    def help(self):
        print("This command does nothing notable")


@command("echo")
class EchoCommand(SimpleCommand):

    def short_help(self) -> str:
        return "Echoes the entire command and arguments"

    def run(self, args: List[str]):
        print(f'Got the following command: {" ".join(args)}')
        if "count" not in self._persistent_data:
            self._persistent_data["count"] = 0
        self._persistent_data[f"arg_{self._persistent_data['count']}"] = " ".join(args)
        self._persistent_data["count"] += 1
        print(self._persistent_data)

    def help(self):
        print("Echoes the supplied command and it's arguments back to the user")


@command("entertestmode")
class EnterTestModeCommand(SimpleCommand):

    def run(self, args: List[str]):
        mode = TestMode(self.handler, "-b" in args)
        self.handler.enter_mode(mode)

    def help(self):
        pass

    def short_help(self) -> str:
        return "Enters a new mode"


class TestMode(Mode):

    def __init__(self, handler, should_halt_exit=False):
        super(TestMode, self).__init__(handler)
        self._block_exit = not should_halt_exit

    def before_execution(self, command) -> bool:
        return True

    def display(self):
        return "Test Mode"

    def enter(self):
        print("Entering test mode")

    def exit(self):
        print("Exiting test mode")
        return self._block_exit
