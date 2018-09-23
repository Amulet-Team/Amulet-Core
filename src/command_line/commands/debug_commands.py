from typing import List

from command_line import SimpleCommand, WorldMode
from command_line.command_api import command, parse_coordinates


@command("get_block")
class GetBlockCommand(SimpleCommand):
    def run(self, args: List[str]):
        if not self.handler.in_mode(WorldMode):
            print("Error: A world must be loaded before this command can be used")
            return

        result = parse_coordinates(f'<{",".join(args[1:4])}>')
        if result is None:
            print("Error: You must supply X, Y, and Z coordinates")
            return

        x, y, z = result

        world = self.get_mode(WorldMode).world

        print(f"Block at ({x}, {y}, {z}): {world.get_block(x,y,z)}")

    def help(self):
        pass

    def short_help(self) -> str:
        return "Gets the blockstate of the specified coordinates"
