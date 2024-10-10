from __future__ import annotations

import collections.abc
import typing

import pybind11_stubgen.typing_ext

__all__ = [
    "BlockMesh",
    "BlockMeshCullDirection",
    "BlockMeshPart",
    "BlockMeshTransparency",
    "FloatVec2",
    "FloatVec3",
    "Triangle",
    "Vertex",
    "merge_block_meshes",
]

class BlockMesh:
    """
    All the data that makes up a block mesh.
    """

    def __init__(
        self,
        transparency: BlockMeshTransparency,
        textures: list[str],
        parts: typing.Annotated[
            list[BlockMeshPart | None], pybind11_stubgen.typing_ext.FixedSize(7)
        ],
    ) -> None: ...
    def rotate(self, rotx: int, roty: int) -> BlockMesh:
        """
        Rotate the mesh in the x and y axis. Accepted values are -3 to 3 which corrospond to 90 degree rotations.
        """

    @property
    def parts(
        self,
    ) -> typing.Annotated[
        list[BlockMeshPart | None], pybind11_stubgen.typing_ext.FixedSize(7)
    ]:
        """
        The mesh parts that make up this mesh. The index corrosponds to the value of BlockMeshCullDirection.
        """

    @parts.setter
    def parts(
        self,
        arg0: typing.Annotated[
            list[BlockMeshPart | None], pybind11_stubgen.typing_ext.FixedSize(7)
        ],
    ) -> None: ...
    @property
    def textures(self) -> list[str]:
        """
        The texture paths used in this block mesh. The Triangle's texture_index attribute is an index into this list.
        """

    @textures.setter
    def textures(self, arg0: list[str]) -> None: ...
    @property
    def transparency(self) -> BlockMeshTransparency:
        """
        The transparency state of this block mesh.
        """

    @transparency.setter
    def transparency(self, arg0: BlockMeshTransparency) -> None: ...

class BlockMeshCullDirection:
    """
    The direction a mesh part is culled by. The value corrosponds to the index in the mesh parts array.

    Members:

      CullNone : Is not culled by any neighbouring blocks.

      CullUp : Is culled by an opaque block above.

      CullDown : Is culled by an opaque block below.

      CullNorth : Is culled by an opaque block to the north.

      CullEast : Is culled by an opaque block to the east.

      CullSouth : Is culled by an opaque block to the south.

      CullWest : Is culled by an opaque block to the west.
    """

    CullDown: typing.ClassVar[
        BlockMeshCullDirection
    ]  # value = <BlockMeshCullDirection.CullDown: 2>
    CullEast: typing.ClassVar[
        BlockMeshCullDirection
    ]  # value = <BlockMeshCullDirection.CullEast: 4>
    CullNone: typing.ClassVar[
        BlockMeshCullDirection
    ]  # value = <BlockMeshCullDirection.CullNone: 0>
    CullNorth: typing.ClassVar[
        BlockMeshCullDirection
    ]  # value = <BlockMeshCullDirection.CullNorth: 3>
    CullSouth: typing.ClassVar[
        BlockMeshCullDirection
    ]  # value = <BlockMeshCullDirection.CullSouth: 5>
    CullUp: typing.ClassVar[
        BlockMeshCullDirection
    ]  # value = <BlockMeshCullDirection.CullUp: 1>
    CullWest: typing.ClassVar[
        BlockMeshCullDirection
    ]  # value = <BlockMeshCullDirection.CullWest: 6>
    __members__: typing.ClassVar[
        dict[str, BlockMeshCullDirection]
    ]  # value = {'CullNone': <BlockMeshCullDirection.CullNone: 0>, 'CullUp': <BlockMeshCullDirection.CullUp: 1>, 'CullDown': <BlockMeshCullDirection.CullDown: 2>, 'CullNorth': <BlockMeshCullDirection.CullNorth: 3>, 'CullEast': <BlockMeshCullDirection.CullEast: 4>, 'CullSouth': <BlockMeshCullDirection.CullSouth: 5>, 'CullWest': <BlockMeshCullDirection.CullWest: 6>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class BlockMeshPart:
    """
    A part of a block mesh for one of the culling directions.
    """

    def __init__(self, verts: list[Vertex], triangles: list[Triangle]) -> None: ...
    @property
    def triangles(self) -> list[Triangle]:
        """
        The triangles in this block mesh part.
        """

    @triangles.setter
    def triangles(self, arg0: list[Triangle]) -> None: ...
    @property
    def verts(self) -> list[Vertex]:
        """
        The vertices in this block mesh part.
        """

    @verts.setter
    def verts(self, arg0: list[Vertex]) -> None: ...

class BlockMeshTransparency:
    """
    The transparency of a block mesh.

    Members:

      FullOpaque : A block that ocupies the whole block and is opaque.

      FullTranslucent : A block that ocupies the whole block and has at least one translucent face.

      Partial : A block that does not ocupy the whole block.
    """

    FullOpaque: typing.ClassVar[
        BlockMeshTransparency
    ]  # value = <BlockMeshTransparency.FullOpaque: 0>
    FullTranslucent: typing.ClassVar[
        BlockMeshTransparency
    ]  # value = <BlockMeshTransparency.FullTranslucent: 1>
    Partial: typing.ClassVar[
        BlockMeshTransparency
    ]  # value = <BlockMeshTransparency.Partial: 2>
    __members__: typing.ClassVar[
        dict[str, BlockMeshTransparency]
    ]  # value = {'FullOpaque': <BlockMeshTransparency.FullOpaque: 0>, 'FullTranslucent': <BlockMeshTransparency.FullTranslucent: 1>, 'Partial': <BlockMeshTransparency.Partial: 2>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class FloatVec2:
    """
    A 2D floating point vector
    """

    x: float
    y: float
    def __init__(self, x: float, y: float) -> None: ...

class FloatVec3:
    """
    A 3D floating point vector
    """

    x: float
    y: float
    z: float
    def __init__(self, x: float, y: float, z: float) -> None: ...

class Triangle:
    """
    The vertex and texture indexes that make up a triangle.
    """

    texture_index: int
    vert_index_a: int
    vert_index_b: int
    vert_index_c: int
    def __init__(
        self,
        vert_index_a: int,
        vert_index_b: int,
        vert_index_c: int,
        texture_index: int,
    ) -> None: ...

class Vertex:
    """
    Attributes for a single vertex.
    """

    def __init__(
        self, coord: FloatVec3, texture_coord: FloatVec2, tint: FloatVec3
    ) -> None: ...
    @property
    def coord(self) -> FloatVec3:
        """
        The spatial coordinate of the vertex.
        """

    @coord.setter
    def coord(self, arg0: FloatVec3) -> None: ...
    @property
    def texture_coord(self) -> FloatVec2:
        """
        The texture coordinate of the vertex.
        """

    @texture_coord.setter
    def texture_coord(self, arg0: FloatVec2) -> None: ...
    @property
    def tint(self) -> FloatVec3:
        """
        The tint colour for the vertex.
        """

    @tint.setter
    def tint(self, arg0: FloatVec3) -> None: ...

def merge_block_meshes(meshes: collections.abc.Sequence[BlockMesh]) -> BlockMesh:
    """
    Merge multiple block mesh objects into one block mesh.
    """
