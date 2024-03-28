# from amulet.palette import BlockPalette
# from amulet.block import BlockStack, Block
# from amulet.version import VersionRange, VersionNumber
# from pickle_db import CustomUnpickler, CustomPickler
# import time
# import pickle
# from amulet_nbt import StringTag
#
#
# def main() -> None:
#     palette = BlockPalette(VersionRange("java", VersionNumber(1), VersionNumber(2)))
#     palette.block_stack_to_index(
#         BlockStack(
#             Block(
#                 "java",
#                 VersionNumber(1, 20),
#         "minecraft",
#         "stone",
#                 {}
#             )
#         )
#     )
#     palette.block_stack_to_index(
#         BlockStack(
#             Block(
#                 "java",
#                 VersionNumber(1, 20),
#                 "minecraft",
#                 "cobblestone",
#                 {}
#             )
#         )
#     )
#     palette.block_stack_to_index(
#         BlockStack(
#             Block(
#                 "java",
#                 VersionNumber(1, 20),
#                 "minecraft",
#                 "stone_brick",
#                 {}
#             )
#         )
#     )
#     palette.block_stack_to_index(
#         BlockStack(
#             Block(
#                 "java",
#                 VersionNumber(1, 20),
#                 "minecraft",
#                 "andesite",
#                 {}
#             )
#         )
#     )
#     for face in ("floor", "wall", "ceiling"):
#         for facing in ("north", "south", "west", "east"):
#             for powered in ("true", "false"):
#                 palette.block_stack_to_index(
#                     BlockStack(
#                         Block(
#                             "java",
#                             VersionNumber(1, 5),
#                             "minecraft",
#                             "acacia_button",
#                             {
#                                 "face": StringTag(face),
#                                 "facing": StringTag(facing),
#                                 "powered": StringTag(powered)
#                             }
#                         )
#                     )
#                 )
#
#     count = 10_000
#     t = time.time()
#     for _ in range(count):
#         binary, constants = CustomPickler.dumps(palette)
#         l2 = CustomUnpickler.loads(binary, constants)
#     print(time.time() - t)
#     t = time.time()
#     for _ in range(count):
#         raw_binary = pickle.dumps(palette)
#         l2 = pickle.loads(raw_binary)
#     print(time.time() - t)
#
#
# if __name__ == '__main__':
#     main()


from pickle_db import CustomUnpickler, CustomPickler
from amulet.level.bedrock import BedrockLevel
import time
import pickle
import copy

level = BedrockLevel.load(
    r"C:\Users\james_000\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds\BXT5ZSe1AgA="
)
level.open()
overworld = level.get_dimension("minecraft:overworld")
chunk_handle = overworld.get_chunk_handle(-15, -43)
chunk = chunk_handle.get()
# raw_overworld = level.raw.get_dimension("minecraft:overworld")
# encoded_chunk = raw_overworld.native_chunk_to_raw_chunk(-15, -43, chunk)
# chunk2 = raw_overworld.raw_chunk_to_native_chunk(-15, -43, encoded_chunk)
# print("hi")


count = 10000
t = time.time()
for _ in range(count):
    binary, constants = CustomPickler.dumps(chunk)
    l2 = CustomUnpickler.loads(binary, constants)
print(time.time() - t)
# t = time.time()
# for _ in range(count):
#     raw_binary = pickle.dumps(chunk)
#     l2 = pickle.loads(raw_binary)
# print(time.time() - t)

# import numpy
# import pickle
# import time
# arr = numpy.random.randint(0, 9999, (16, 16, 16), numpy.uint32)
# count = 100_000
# t = time.time()
# for _ in range(count):
#     raw_binary = pickle.dumps(arr)
#     arr2 = pickle.loads(raw_binary)
# print(time.time() - t)
# print("done")
