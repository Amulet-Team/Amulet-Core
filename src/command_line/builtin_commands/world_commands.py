from __future__ import annotations

from typing import List

from command_line import ComplexCommand, command, subcommand, WorldMode

from api.world_loader import loader

from api.errors import (
    FormatError,
    FormatLoaderInvalidFormat,
    FormatLoaderMismatched,
    FormatLoaderNoneMatched,
)


@command("world")
class WorldCommand(ComplexCommand):
    @subcommand("load")
    def load(self, args: List[str]):
        world_path: str = None
        intent_format: str = None
        intent_forced: str = False

        for arg in args[1:]:
            if arg.startswith("--format="):
                intent_format = arg[9:]
            elif arg == "--force":
                intent_forced = True
            else:
                world_path = arg

        if world_path is None:
            print('Usage: world.load "<world_path>"')
            return

        try:
            world_mode = WorldMode(
                self.handler,
                world=world_path,
                world_format=intent_format,
                forced=intent_forced,
            )

            self.handler.enter_mode(world_mode)
        except (FormatLoaderInvalidFormat, FormatLoaderNoneMatched) as e:
            print(f"==== Error: {e}")
            print(f"Available formats: {loader.get_loaded_identifiers()}")
            print("Use --format=<world format> to specify a specific format")
        except FormatLoaderMismatched as e:
            print(f"==== Error: {e}")
            print("Use --force to override")

    @subcommand("unload")
    def unload(self, args: List[str]):
        if self.handler.in_mode(WorldMode):
            self.handler.exit_mode()
        else:
            print(
                "=== Error: You must have opened a Minecraft world before unloading it"
            )

    @subcommand("identify")
    def identify(self, args: List[str]):
        try:
            if not self.handler.in_mode(WorldMode):
                if len(args) == 1:
                    print('Usage: world.identify "<world filepath>"')
                    return

                version, identified_format = loader.identify(args[1])
            elif len(args) == 2:
                version, identified_format = loader.identify(args[1])
            else:
                world_mode = self.get_mode(WorldMode)
                version, identified_format = loader.identify(world_mode.world_path)

            print(f"Version: {version.replace('_', '.')}")
            print(f"Format: {identified_format}")
        except FormatError as e:
            print(f"==== Error: {e}")

    @classmethod
    def help(cls, command_name: str = None):
        if command_name == "load":
            print("Loads a Minecraft world and enters World Mode")
            print("This command cannot be used once the program")
            print("has entered a World Mode\n")
            print('Usage: world.load "<world filepath>"')
        elif command_name == "identify":
            print("Identifies what format the given Minecraft world is in")
            print("This command can be used in 2 ways. The first method")
            print("is to supply a filepath to the world directory along")
            print("with the command itself. The second method is by loading")
            print("a world then running the command without any arguments.")
            print("However, if an argument is given, the format of the given path")
            print("will be displayed\n")
            print('Usage: world.identify "<world filepath>"')
            print("Usage (When in World Mode): world.identify")
        elif command_name == "unload":
            print("Unloads the currently opened Minecraft world\n")
            print("Usage: world.unload")
        else:
            print("load - Loads a Minecraft world with the appropriate format loader")
            print("identify - Prints out the identified loader for a given world")
            print("unload - Unloads the currently opened Minecraft world")

    @classmethod
    def short_help(cls) -> str:
        return "Various commands for loading and modifying worlds"
