import numpy
from _typeshed import Incomplete
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer as SubChunkArrayContainer
from amulet.palette import BiomePalette as BiomePalette
from amulet.version import VersionRange as VersionRange
from numpy.typing import ArrayLike as ArrayLike
from typing import Iterable, Union

class Biome3DComponent:
    __biome_palette: Incomplete
    __biomes: Incomplete
    def __init__(self, version_range: VersionRange, array_shape: tuple[int, int, int], default_array: Union[int, ArrayLike]) -> None: ...
    @property
    def biome(self) -> SubChunkArrayContainer: ...
    @biome.setter
    def biome(self, sections: Iterable[int, ArrayLike]): ...
    @property
    def biome_palette(self): ...

class Biome2DComponent:
    __array_shape: Incomplete
    __biome_palette: Incomplete
    def __init__(self, version_range: VersionRange, array_shape: tuple[int, int], array: Union[int, ArrayLike]) -> None: ...
    @property
    def biome(self) -> numpy.ndarray: ...
    __biomes: Incomplete
    @biome.setter
    def biome(self, array: Union[int, ArrayLike]): ...
    @property
    def biome_palette(self): ...
