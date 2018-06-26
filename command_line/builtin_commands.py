from typing import Sequence, List, Type
import os

from api.cmd_line import SimpleCommand, ComplexCommand, Mode
from api.data_structures import SimpleStack

from formats.format_loader import loader


class WorldMode(Mode):

    def __init__(self, cmd_line_handler, **kwargs):
        super(WorldMode, self).__init__(cmd_line_handler)
        self._world_path = kwargs.get("world")
        self._world_name = os.path.basename(self._world_path)
        self._unsaved_changes = SimpleStack()

    def display(self) -> str:
        return self._world_name

    def before_execution(self, command) -> bool:
        if command[0] == "load" and not self._unsaved_changes.is_empty():
            print("You can't load a new world if you currently have unsaved changes")
            return False
        return True

    def enter(self):
        if __debug__:
            print("Entered world mode")

    def exit(self):
        if not self._unsaved_changes.is_empty():
            print("You have unsaved changes, do you really want to quit?")
            ans = input("(y/n)> ")
            if ans == "y":
                return True
            return False
        return True


class WorldCommand(ComplexCommand):

    base = "world"

    @classmethod
    def get_children(cls) -> Sequence[Type[SimpleCommand]]:
        return WorldLoadCommand, WorldIdentifyCommand

    @classmethod
    def help(cls):
        print("===== World Commands =====")
        print("load - Loads a Minecraft world with the appropriate format loader")
        print("identify - Prints out the identified loader for a given world")

    @classmethod
    def short_help(cls) -> str:
        return "Various commands for loading and modifying worlds"


class WorldLoadCommand(SimpleCommand):

    command = "load"

    def run(self, args: List[str]):
        print(args)
        world_path = args[1]
        world_mode = WorldMode(self.handler, world=world_path)
        self.handler.enter_mode(world_mode)

    def help(self):
        pass

    def short_help(self) -> str:
        return ""


class WorldIdentifyCommand(SimpleCommand):

    command = "identify"

    def run(self, args: List[str]):
        identified_format = loader.identify_world_format_str(args[1])
        print(f"Format: {identified_format}")

    def help(self):
        pass

    def short_help(self) -> str:
        return ""
