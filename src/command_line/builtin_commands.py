from typing import Sequence, List, Type
import os

from command_line import SimpleCommand, ComplexCommand, Mode
from api.data_structures import SimpleStack

from formats.format_loader import loader
from api.world import World


class WorldMode(Mode):

    def __init__(self, cmd_line_handler, **kwargs):
        super(WorldMode, self).__init__(cmd_line_handler)
        self._world_path = kwargs.get("world")
        self._world_name = os.path.basename(self._world_path)
        self._unsaved_changes = SimpleStack()
        self._world = loader.load_world(self._world_path)

    @property
    def world_path(self) -> str:
        return self._world_path

    @property
    def world(self) -> World:
        return self._world

    def display(self) -> str:
        return self._world_name

    def before_execution(self, command) -> bool:
        if command[0] == "load" and not self._unsaved_changes.is_empty():
            print("You can't load a new world if you currently have unsaved changes")
            return False

        return True

    def enter(self) -> bool:
        if self.handler.in_mode(WorldMode):
            print("You cannot load a world if another world is already loaded!")
            return False

        if __debug__:
            print("Entered world mode")
        return True

    def exit(self) -> bool:
        if __debug__:
            print("Exiting world mode")
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
        return WorldLoadCommand, WorldIdentifyCommand, WorldUnloadCommand

    @classmethod
    def help(cls):
        print("load - Loads a Minecraft world with the appropriate format loader")
        print("identify - Prints out the identified loader for a given world")
        print("unload - Unloads the currently opened Minecraft world")

    @classmethod
    def short_help(cls) -> str:
        return "Various commands for loading and modifying worlds"


class WorldLoadCommand(SimpleCommand):

    command = "load"

    def run(self, args: List[str]):
        if len(args) == 1:
            print('Usage: world.load "<world filepath>"')
            return

        world_path = args[1]
        world_mode = WorldMode(self.handler, world=world_path)
        self.handler.enter_mode(world_mode)

    def help(self):
        print("Loads a Minecraft world and enters World Mode")
        print("This command cannot be used once the program")
        print("has entered a World Mode\n")
        print('Usage: world.load "<world filepath>"')

    def short_help(self) -> str:
        return "Loads a Minecraft world and enters World Mode"


class WorldUnloadCommand(SimpleCommand):

    command = "unload"

    def run(self, args: List[str]):
        if self.handler.in_mode(WorldMode):
            self.handler.exit_mode()
        else:
            print(
                "=== Error: You must have opened a Minecraft world before unloading it"
            )

    def help(self):
        print("Unloads the currently opened Minecraft world")

    def short_help(self) -> str:
        return "Unloads the currently opened Minecraft world"


class WorldIdentifyCommand(SimpleCommand):

    command = "identify"

    def run(self, args: List[str]):
        if not self.handler.in_mode(WorldMode):
            if len(args) == 1:
                print('Usage: world.identify "<world filepath>"')
                return

            identified_format = loader.identify_world_format_str(args[1])
        elif len(args) == 2:
            identified_format = loader.identify_world_format_str(args[1])
        else:
            world_mode = self.handler.get_mode(WorldMode)
            identified_format = loader.identify_world_format_str(world_mode.world_path)

        print(f"Format: {identified_format}")

    def help(self):
        print("Identifies what format the given Minecraft world is in")
        print("This command can be used in 2 ways. The first method")
        print("is to supply a filepath to the world directory along")
        print("with the command itself. The second method is by loading")
        print("a world then running the command without any arguments.")
        print("However, if an argument is given, the format of the given path")
        print("will be displayed\n")
        print('Usage: world.identify "<world filepath>"')
        print("Usage (When in World Mode): world.identify")

    def short_help(self) -> str:
        return "Identifies what format the given Minecraft world is in"
