from amulet.selection import SelectionBox, SelectionGroup

LOCAL_PLAYER = "~local_player"
OVERWORLD = "minecraft:overworld"
THE_NETHER = "minecraft:the_nether"
THE_END = "minecraft:the_end"
DefaultSelection = SelectionGroup(
    SelectionBox((-30_000_000, 0, -30_000_000), (30_000_000, 256, 30_000_000))
)
