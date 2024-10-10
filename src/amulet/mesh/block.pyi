from __future__ import annotations

import typing

import pybind11_stubgen.typing_ext

__all__ = [
    "BlockMesh",
    "BlockMeshPart",
    "CullDirection",
    "FloatVec2",
    "FloatVec3",
    "Transparency",
    "Triangle",
    "Vertex",
]

class BlockMesh:
    parts: typing.Annotated[
        list[BlockMeshPart | None], pybind11_stubgen.typing_ext.FixedSize(7)
    ]
    textures: list[str]
    transparency: Transparency
    def __init__(
        self,
        transparency: Transparency,
        textures: list[str],
        parts: typing.Annotated[
            list[BlockMeshPart | None], pybind11_stubgen.typing_ext.FixedSize(7)
        ],
    ) -> None: ...
    def rotate(self, rotx: int, roty: int) -> BlockMesh: ...

class BlockMeshPart:
    triangles: list[Triangle]
    verts: list[Vertex]
    def __init__(self, verts: list[Vertex], triangles: list[Triangle]) -> None: ...

class CullDirection:
    """
    Members:

      CullNone

      CullUp

      CullDown

      CullNorth

      CullEast

      CullSouth

      CullWest
    """

    CullDown: typing.ClassVar[CullDirection]  # value = <CullDirection.CullDown: 2>
    CullEast: typing.ClassVar[CullDirection]  # value = <CullDirection.CullEast: 4>
    CullNone: typing.ClassVar[CullDirection]  # value = <CullDirection.CullNone: 0>
    CullNorth: typing.ClassVar[CullDirection]  # value = <CullDirection.CullNorth: 3>
    CullSouth: typing.ClassVar[CullDirection]  # value = <CullDirection.CullSouth: 5>
    CullUp: typing.ClassVar[CullDirection]  # value = <CullDirection.CullUp: 1>
    CullWest: typing.ClassVar[CullDirection]  # value = <CullDirection.CullWest: 6>
    __members__: typing.ClassVar[
        dict[str, CullDirection]
    ]  # value = {'CullNone': <CullDirection.CullNone: 0>, 'CullUp': <CullDirection.CullUp: 1>, 'CullDown': <CullDirection.CullDown: 2>, 'CullNorth': <CullDirection.CullNorth: 3>, 'CullEast': <CullDirection.CullEast: 4>, 'CullSouth': <CullDirection.CullSouth: 5>, 'CullWest': <CullDirection.CullWest: 6>}
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
    x: float
    y: float
    def __init__(self, x: float, y: float) -> None: ...

class FloatVec3:
    x: float
    y: float
    z: float
    def __init__(self, x: float, y: float, z: float) -> None: ...

class Transparency:
    """
    Members:

      FullOpaque

      FullTranslucent

      Partial
    """

    FullOpaque: typing.ClassVar[Transparency]  # value = <Transparency.FullOpaque: 0>
    FullTranslucent: typing.ClassVar[
        Transparency
    ]  # value = <Transparency.FullTranslucent: 1>
    Partial: typing.ClassVar[Transparency]  # value = <Transparency.Partial: 2>
    __members__: typing.ClassVar[
        dict[str, Transparency]
    ]  # value = {'FullOpaque': <Transparency.FullOpaque: 0>, 'FullTranslucent': <Transparency.FullTranslucent: 1>, 'Partial': <Transparency.Partial: 2>}
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

class Triangle:
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
    coord: FloatVec3
    texture_coord: FloatVec2
    tint: FloatVec3
    def __init__(
        self, coord: FloatVec3, texture_coord: FloatVec2, tint: FloatVec3
    ) -> None: ...
