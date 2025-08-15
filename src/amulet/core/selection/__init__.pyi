from __future__ import annotations

from amulet.core.selection.box import SelectionBox
from amulet.core.selection.box_group import SelectionBoxGroup
from amulet.core.selection.box_group import SelectionBoxGroup as SelectionGroup
from amulet.core.selection.shape import SelectionShape

from . import box, box_group, group, shape

__all__: list[str] = [
    "SelectionBox",
    "SelectionBoxGroup",
    "SelectionGroup",
    "SelectionShape",
    "box",
    "box_group",
    "group",
    "shape",
]
