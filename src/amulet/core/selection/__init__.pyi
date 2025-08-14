from __future__ import annotations

from amulet.core.selection.box import SelectionBox
from amulet.core.selection.boxes import SelectionBoxes
from amulet.core.selection.boxes import SelectionBoxes as SelectionGroup

from . import box, boxes, group

__all__: list[str] = [
    "SelectionBox",
    "SelectionBoxes",
    "SelectionGroup",
    "box",
    "boxes",
    "group",
]
