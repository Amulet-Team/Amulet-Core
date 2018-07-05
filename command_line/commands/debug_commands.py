from typing import List

import world_utils
from api.cmd_line import SimpleCommand
from command_line.builtin_commands import WorldMode


class GetBlockCommand(SimpleCommand):

    command = "get_block"

    def run(self, args: List[str]):
        if not self.handler.in_mode(WorldMode):
            print("Error: A world must be loaded before this command can be used")
            return

        try:
            x, y, z = map(int, args[1:4])
        except IndexError:
            print("Error: You must supply X, Y, and Z coordinates")
            return

        id_format = "normal"
        if len(args) == 5:
            if args[4].lower() == "internal":
                id_format = "internal"

        # Do this the long way since the UnifiedFormat class isn't complete
        """
        cx, cz = world_utils.block_coords_to_chunk_coords(x, z)

        world_mode = self.handler.get_mode(WorldMode)
        world = world_mode.world
        blocks, d1, d2 = world.d_load_chunk(cx, cz)

        true_x, true_z = x - cx * 16, z - cz * 16

        block = blocks[true_x, y, true_z]
        """
        world_mode = self.handler.get_mode(WorldMode)
        world = world_mode.world

        if id_format == "internal":
            print(f"Block at ({x}, {y}, {z}): {world.get_block(x,y,z)}")
        else:
            name = world.mapping_handler.get_entry(world.get_block(x, y, z))
            print(f"Block at ({x}, {y}, {z}): {name}")

    def help(self):
        pass

    def short_help(self) -> str:
        return "Gets the internal block ID of the specified coords"
