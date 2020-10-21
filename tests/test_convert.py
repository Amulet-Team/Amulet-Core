import sys
import numpy
import os
import shutil

from amulet.world_interface import load_world, load_format
from amulet.api.block import Block, UniversalAirBlock
from amulet.api.chunk import Chunk


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print("Command line arguments required")
        print("random_chunk <origin_world_path> <cx> <cz>")
        print("convert <origin_world_path> <destination_world_path>")
    elif len(args) >= 1:
        mode = args[0]
        if mode in ["random_chunk", "air", "stone"]:
            if len(args) >= 4:
                world_path = args[1]
                cx, cz = int(args[2]), int(args[3])

                print(f"Loading world at {world_path}")
                world = load_world(world_path)
                print(f"Loading chunk at {cx}, {cz}")
                chunk = world.get_chunk(cx, cz)
                print("A vertical column of blocks in the chunk:")
                for block in chunk.blocks[
                    0, :, 0
                ].ravel():  # the blockstates of one vertical column
                    print(world.block_palette[block])
                air = world.block_palette.get_add_block(UniversalAirBlock)
                print("Filling chunk with blocks")
                if mode == "air":
                    chunk.blocks[0, 0, 0] = air
                elif mode == "random_chunk":
                    blocks = numpy.random.randint(
                        0, len(world.block_palette.blocks()), size=(16, 256, 16)
                    )
                    for index, block in enumerate(world.block_palette.blocks()):
                        if block.base_name in ["lava", "water"]:
                            blocks[blocks == index] = air
                    chunk.blocks[:, :, :] = blocks
                elif mode == "stone":
                    chunk.blocks[:, :, :] = world.block_palette.get_add_block(
                        Block(namespace="universal_minecraft", base_name="stone")
                    )
                chunk.changed = True
                print("Saving world")
                world.save()
                world.close()

                print("Reloading world and printing new blocks")
                world = load_world(world_path)
                chunk = world.get_chunk(cx, cz)
                for block in chunk.blocks[
                    0, :, 0
                ].ravel():  # the blockstates of one vertical column
                    print(world.block_palette[block])
            else:
                print("Not enough arguments given. Format must be:")
                print("random_chunk/air <origin_world_path> <cx> <cz>")

        elif mode == "convert":
            if len(args) >= 3:
                world_path = args[1]
                destination_path = args[2]

                print(f"Loading world at {world_path}")
                world = load_world(world_path)
                output_wrapper = load_format(destination_path)
                output_wrapper.open()
                world.save(output_wrapper)
                world.close()
                output_wrapper.close()
            else:
                print("Not enough arguments given. Format must be:")
                print("convert <origin_world_path> <destination_world_path>")

        elif mode == "delete_chunk":
            if len(args) >= 4:
                world_path = args[1]
                cx, cz = int(args[2]), int(args[3])

                print(f"Loading world at {world_path}")
                world = load_world(world_path)
                world.delete_chunk(cx, cz)
                print("Saving world")
                world.save()
                world.close()
            else:
                print("Not enough arguments given. Format must be:")
                print("delete_chunk <origin_world_path> <cx> <cz>")
        elif mode == "self_convert":
            if len(args) >= 2:
                world_path = args[1]
                ext = 0
                while os.path.exists(f"{world_path}_{ext}"):
                    ext += 1
                source_path = f"{world_path}_{ext}"
                shutil.copytree(world_path, source_path)

                while os.path.exists(f"{world_path}_{ext}"):
                    ext += 1
                destination_path = f"{world_path}_{ext}"
                shutil.copytree(world_path, destination_path)

                print(f"Loading world at {source_path}")
                world = load_world(source_path)
                for chunk in list(world.world_wrapper.all_chunk_coords()):
                    if max(abs(chunk[0]), abs(chunk[1])) > 5:
                        world.delete_chunk(*chunk)
                world.save()
                for cx, cz in world.world_wrapper.all_chunk_coords():
                    chunk = world.get_chunk(cx, cz)
                    chunk.blocks[0, :, 0] = world.block_palette.get_add_block(
                        Block(namespace="universal_minecraft", base_name="stone")
                    )
                    chunk.blocks[0, :, 15] = world.block_palette.get_add_block(
                        Block(namespace="universal_minecraft", base_name="stone")
                    )
                    chunk.blocks[15, :, 0] = world.block_palette.get_add_block(
                        Block(namespace="universal_minecraft", base_name="stone")
                    )
                    chunk.blocks[15, :, 15] = world.block_palette.get_add_block(
                        Block(namespace="universal_minecraft", base_name="stone")
                    )
                world.save()

                output_wrapper = load_format(destination_path)
                output_wrapper.open()
                for chunk in list(output_wrapper.all_chunk_coords()):
                    output_wrapper.delete_chunk(*chunk)
                output_wrapper.save()

                world.save(output_wrapper)
                world.close()
                output_wrapper.close()
            else:
                print("Not enough arguments given. Format must be:")
                print("convert <origin_world_path> <destination_world_path>")

        elif mode == "create":
            if len(args) >= 4:
                world_path = args[1]
                cx, cz = int(args[2]), int(args[3])

                print(f"Loading world at {world_path}")
                world = load_world(world_path)
                if (cx, cz) in world.world_wrapper.all_chunk_coords():
                    world.delete_chunk(*(cx, cz))
                world.save()

                chunk = Chunk(cx, cz)
                bedrock = world.block_palette.get_add_block(
                    Block(namespace="universal_minecraft", base_name="bedrock")
                )
                stone = world.block_palette.get_add_block(
                    Block(namespace="universal_minecraft", base_name="stone")
                )
                dirt = world.block_palette.get_add_block(
                    Block(namespace="universal_minecraft", base_name="dirt")
                )
                grass = world.block_palette.get_add_block(
                    Block(namespace="universal_minecraft", base_name="grass_block")
                )

                chunk.blocks[:, 0, :] = bedrock
                chunk.blocks[:, 1:3, :] = stone
                chunk.blocks[:, 3:6, :] = dirt
                chunk.blocks[:, 6, :] = grass

                world.put_chunk(chunk)

                world.save()
                world.close()
            else:
                print("Not enough arguments given. Format must be:")
                print("convert <origin_world_path> <destination_world_path>")

        else:
            print(f'Unknown mode "{mode}"')
