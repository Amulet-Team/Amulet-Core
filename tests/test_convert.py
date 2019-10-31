import sys
import numpy

from amulet.world_interface import load_world, load_format
from amulet.api.block import Block


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print("Command line arguments required")
        print("random_chunk <origin_world_path> <cx> <cz>")
        print("convert <origin_world_path> <destination_world_path>")
    elif len(args) >= 1:
        mode = args[0]
        if mode == "random_chunk":
            if len(args) >= 4:
                world_path = args[1]
                cx, cz = int(args[2]), int(args[3])

                print(f"Loading world at {world_path}")
                world = load_world(world_path)
                print(f"Loading chunk at {cx}, {cz}")
                chunk = world.get_chunk(cx, cz)
                print("A vertical column of blocks in the chunk:")
                for block in chunk.blocks.ravel()[
                    :4096:16
                ]:  # the blockstates of one vertical column
                    print(world.palette[block])
                air = world.palette.get_add_block(
                    Block(namespace="universal_minecraft", base_name="air")
                )
                # blocks[0, 30, 0] = stone
                # c.blocks = numpy.full((16, 256, 16), stone)
                print("Filling chunk with blocks")
                blocks = numpy.random.randint(
                    0, len(world.palette.blocks()), size=(16, 256, 16)
                )
                for index, block in enumerate(world.palette.blocks()):
                    if block.base_name in ["lava", "water"]:
                        blocks[blocks == index] = air
                chunk.blocks = blocks
                print("Saving world")
                world.save()
                world.close()

                print("Reloading world and printing new blocks")
                world = load_world(world_path)
                chunk = world.get_chunk(cx, cz)
                for block in chunk.blocks.ravel()[
                    :4096:16
                ]:  # the blockstates of one vertical column
                    print(world.palette[block])
            else:
                print("Not enough arguments given. Format must be:")
                print("random_chunk <origin_world_path> <cx> <cz>")

        elif mode == "convert":
            if len(args) >= 3:
                world_path = args[1]
                destination_path = args[2]

                print(f"Loading world at {world_path}")
                world = load_world(world_path)
                output_wrapper = load_format(destination_path)
                world.save(output_wrapper)
                world.close()
                output_wrapper.close()
            else:
                print("Not enough arguments given. Format must be:")
                print("convert <origin_world_path> <destination_world_path>")
        else:
            print(f'Unknown mode "{mode}"')
