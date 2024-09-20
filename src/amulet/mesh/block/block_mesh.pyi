from collections.abc import Iterable
from enum import IntEnum
from typing import Any

import numpy
from _typeshed import Incomplete
from amulet.mesh.util import rotate_3d as rotate_3d

FACE_KEYS: Incomplete
cull_remap_all: Incomplete

class Transparency(IntEnum):
    FullOpaque: int
    FullTranslucent: int
    Partial: int

class BlockMesh:
    """Class for storing model data"""

    @classmethod
    def merge(cls, models: Iterable[BlockMesh]) -> BlockMesh: ...
    def __init__(
        self,
        face_width: int,
        verts: dict[str | None, numpy.ndarray],
        texture_coords: dict[str | None, numpy.ndarray],
        tint_verts: dict[str | None, numpy.ndarray],
        faces: dict[str | None, numpy.ndarray],
        texture_index: dict[str | None, numpy.ndarray],
        textures: tuple[str, ...],
        transparency: Transparency,
    ) -> None:
        """

        :param face_width: the number of vertices per face (3 or 4)
        :param verts: a numpy float array containing the vert data. One line per vertex
        :param texture_coords: a numpy float array containing the texture coordinate data. One line per vertex
        :param tint_verts: a numpy bool array if the vertex should have a tint applied to it. One line per vertex
        :param faces: a dictionary of numpy int arrays (stored under cull direction) containing
            the vertex indexes (<face_width> columns) and
            texture index (1 column)
        :param texture_index:
        :param textures:
        :param transparency: is the model a full non-transparent block

        Workflow:
            find the directions a block is not being culled in
            look them up in the face table
            the face table will tell you which vertices are needed for the face
        """

    @property
    def face_mode(self) -> int:
        """The number of vertices per face"""

    @property
    def vert_tables(self) -> dict[str | None, numpy.ndarray]:
        """A dictionary of cull dir -> the flat vert table containing vertices, texture coords and (in the future) normals"""

    @property
    def verts(self) -> dict[str | None, numpy.ndarray]:
        """A dictionary mapping face cull direction to the vertex table for that direction.
        The vertex table is a flat numpy array who's length is a multiple of 3.
        x,y,z coordinates."""

    @property
    def texture_coords(self) -> dict[str | None, numpy.ndarray]:
        """A dictionary mapping face cull direction to the texture coords table for that direction.
        The texture coords table is a flat numpy array who's length is a multiple of 2.
        tx, ty"""

    @property
    def tint_verts(self) -> dict[str | None, numpy.ndarray]:
        """A dictionary mapping face cull direction to the tint table for that direction.
        The tint table is a flat numpy bool array with three values per vertex.
        """

    @property
    def faces(self) -> dict[str | None, numpy.ndarray]:
        """A dictionary mapping face cull direction to the face table for that direction.
        The face table is a flat numpy array of multiple 3 or 4 depending on face_mode.
        First 3 or 4 columns index into the verts table.
        Last column indexes into textures."""

    @property
    def texture_index(self) -> dict[str | None, numpy.ndarray]:
        """A dictionary mapping face cull direction to the face table for that direction.
        The face table is a flat numpy array of multiple 2 indexing into textures."""

    @property
    def textures(self) -> tuple[str, ...]:
        """A list of all the texture paths."""

    @property
    def is_opaque(self) -> bool:
        """
        If the model covers all surrounding blocks.
        Also takes into account texture transparency.
        """

    @property
    def is_transparent(self) -> Transparency:
        """
        The transparency mode of the block
        0 - the block is a full block with opaque textures
        1 - the block is a full block with transparent/translucent textures
        2 - the block is not a full block
        """

    def rotate(self, rotx: int, roty: int) -> BlockMesh:
        """Create a rotated version of this block model. Culling directions are also rotated.
        rotx and roty must be ints in the range -3 to 3 inclusive."""

    def __eq__(self, other: Any) -> bool: ...
