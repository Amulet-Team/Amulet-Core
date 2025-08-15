from __future__ import annotations

from amulet.core.selection.box import SelectionBox
from amulet.core.selection.box_group import SelectionBoxGroup
from amulet.core.selection.box_group import SelectionBoxGroup as SelectionGroup
from amulet.core.selection.shape import SelectionShape
from amulet.core.selection.shape_group import SelectionShapeGroup
from amulet.core.selection.sphere import SelectionSphere

from . import box, box_group, group, shape, shape_group, sphere

__all__: list[str] = [
    "SelectionBox",
    "SelectionBoxGroup",
    "SelectionGroup",
    "SelectionShape",
    "SelectionShapeGroup",
    "SelectionSphere",
    "box",
    "box_group",
    "group",
    "shape",
    "shape_group",
    "sphere",
]
