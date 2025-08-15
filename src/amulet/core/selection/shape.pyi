from __future__ import annotations

import amulet.core.selection.box

__all__: list[str] = ["SelectionShape"]

class SelectionShape:
    """
    A base class for selection classes.
    """

    def voxelise(self) -> set[amulet.core.selection.box.SelectionBox]:
        """
        Convert the shape into unit voxels.
        """
