from __future__ import annotations
from amulet.selection.box import SelectionBox
import amulet.selection.group
from amulet.selection.group import SelectionGroup

__all__ = [
    "DefaultSelection",
    "OVERWORLD",
    "SelectionBox",
    "SelectionGroup",
    "THE_END",
    "THE_NETHER",
]
DefaultSelection: (
    amulet.selection.group.SelectionGroup
)  # value = SelectionGroup([SelectionBox((-30000000, 0, -30000000), (30000000, 256, 30000000))])
OVERWORLD: str = "minecraft:overworld"
THE_END: str = "minecraft:the_end"
THE_NETHER: str = "minecraft:the_nether"
