from __future__ import annotations

import types
import typing

import amulet.core.selection.box_group
import amulet.utils.matrix

__all__: list[str] = ["SelectionShape"]

class SelectionShape:
    """
    A base class for selection classes.
    """

    __hash__: typing.ClassVar[None] = None  # type: ignore
    matrix: amulet.utils.matrix.Matrix4x4
    @staticmethod
    def deserialise(s: str) -> SelectionShape:
        """
        Deserialise the serialised data back to an object.
        """

    @typing.overload
    def __eq__(self, other: SelectionShape) -> bool: ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> bool | types.NotImplementedType: ...
    def almost_equal(self, other: SelectionShape) -> bool:
        """
        Check if this shape is equal or almost equal to another shape.
        """

    def serialise(self) -> str:
        """
        Convert the class to human readable plain text.
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

    def voxelise(self) -> amulet.core.selection.box_group.SelectionBoxGroup:
        """
        Convert the selection to a SelectionBoxGroup.
        """
