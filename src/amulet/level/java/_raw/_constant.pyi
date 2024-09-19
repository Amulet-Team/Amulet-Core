from __future__ import annotations

import amulet.selection.group
from amulet.selection.box import SelectionBox
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
OVERWORLD: str
THE_END: str
THE_NETHER: str
