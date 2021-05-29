import amulet
from amulet.api.block import Block

# load the level
level = amulet.load_level("level")

# pick a game version that we want to work with.
# see the next page to see what versions are available.
game_version = ("bedrock", (1, 16, 20))  # the version that we want the block data in.

# get a block
block, block_entity = level.get_version_block(
    0,  # x location
    70,  # y location
    0,  # z location
    "minecraft:overworld",  # dimension
    game_version,
)

if isinstance(block, Block):
    # Check that what we have is actually a block.
    # There are some edge cases such as item frames where the returned value might not be a Block.
    print(block)
    # Block(minecraft:air)

# set a block
# define a block in the format of the version we want to work with.
block = Block("minecraft", "stone")
level.set_version_block(
    0,  # x location
    70,  # y location
    0,  # z location
    "minecraft:overworld",  # dimension
    game_version,
    block,
)

# save the changes to the world
level.save()

# close the world
level.close()
