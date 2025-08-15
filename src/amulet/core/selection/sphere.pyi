from __future__ import annotations

import typing

import amulet.core.selection.shape

__all__: list[str] = ["SelectionSphere"]

class SelectionSphere(amulet.core.selection.shape.SelectionShape):
    """
    The SelectionSphere class represents a single spherical selection.
    """

    def __init__(
        self,
        x: typing.SupportsFloat,
        y: typing.SupportsFloat,
        z: typing.SupportsFloat,
        radius: typing.SupportsFloat,
    ) -> None: ...
    def translate(
        self,
        dx: typing.SupportsFloat,
        dy: typing.SupportsFloat,
        dz: typing.SupportsFloat,
    ) -> SelectionSphere:
        """
        Create a new :class:`SelectionSphere` based on this one with the coordinates moved by the given offset.

        :param dx: The x offset.
        :param dy: The y offset.
        :param dz: The z offset.
        :return: The new selection with the given offset.
        """

    @property
    def radius(self) -> float: ...
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...
    @property
    def z(self) -> float: ...
