from typing import Sequence, List, Type

from command_line import ComplexCommand, SimpleCommand, Mode

from formats.format_loader import loader


class WorldMode(Mode):

    def __init__(self, cmd_line_handler, **kwargs):
        super(WorldMode, self).__init__(cmd_line_handler)

    def display(self) -> str:
        pass


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
