from __future__ import annotations

import typing

import amulet.core.selection.box
import amulet.utils.matrix

__all__: list[str] = ["SelectionShape"]

class SelectionShape:
    """
    A base class for selection classes.
    """

    matrix: amulet.utils.matrix.Matrix4x4
    def almost_equal(self, other: SelectionShape) -> bool:
        """
        Check if this shape is equal or almost equal to another shape.
        """

    def transform(self, matrix: amulet.utils.matrix.Matrix4x4) -> SelectionShape:
        """
        Translate the shape by the given matrix
        """

    def translate(
        self,
        dx: typing.SupportsFloat,
        dy: typing.SupportsFloat,
        dz: typing.SupportsFloat,
    ) -> SelectionShape:
        """
        Translate the shape by the given amount
        """

    def voxelise(self) -> set[amulet.core.selection.box.SelectionBox]:
        """
        Convert the shape into unit voxels.
        """
