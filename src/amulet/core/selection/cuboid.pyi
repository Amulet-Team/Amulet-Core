from __future__ import annotations

import typing

import amulet.core.selection.shape
import amulet.utils.matrix

__all__: list[str] = ["SelectionCuboid"]

class SelectionCuboid(amulet.core.selection.shape.SelectionShape):
    """
    The SelectionCuboid class represents a single spherical selection.
    """

    @typing.overload
    def __init__(
        self,
        min_x: typing.SupportsFloat,
        min_y: typing.SupportsFloat,
        min_z: typing.SupportsFloat,
        size_x: typing.SupportsFloat,
        size_y: typing.SupportsFloat,
        size_z: typing.SupportsFloat,
    ) -> None: ...
    @typing.overload
    def __init__(self, matrix: amulet.utils.matrix.Matrix4x4) -> None: ...
    def __repr__(self) -> str: ...
    def transform(self, matrix: amulet.utils.matrix.Matrix4x4) -> SelectionCuboid:
        """
        Create a new :class:`SelectionCuboid` based on this one transformed by the given matrix.

        :param matrix: The matrix to transform by.
        :return: The new selection with the added transform.
        """

    def translate(
        self,
        dx: typing.SupportsFloat,
        dy: typing.SupportsFloat,
        dz: typing.SupportsFloat,
    ) -> SelectionCuboid:
        """
        Create a new :class:`SelectionCuboid` based on this one with the coordinates moved by the given offset.

        :param dx: The x offset.
        :param dy: The y offset.
        :param dz: The z offset.
        :return: The new selection with the given offset.
        """
