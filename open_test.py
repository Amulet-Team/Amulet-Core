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

blocks = chunk.block_palette
t = time.time()
for _ in range(10_000):
    bin = copy.deepcopy(blocks)
print(time.time()-t)
