from typing import Union, Iterable

import numpy
from numpy.typing import ArrayLike

from amulet.palette import BiomePalette
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer


class Biome3DChunk:
    def __init__(
        self,
        array_shape: tuple[int, int, int],
        default_array: Union[int, ArrayLike],
    ):
        self.__biome_palette = BiomePalette()
        self.__biomes = SubChunkArrayContainer(array_shape, default_array)

    @property
    def biome(self) -> SubChunkArrayContainer:
        return self.__biomes

    @biome.setter
    def biome(
        self,
        sections: Iterable[int, ArrayLike],
    ):
        self.__biomes = SubChunkArrayContainer(
            self.__biomes.array_shape, self.__biomes.default_array, sections
        )

    @property
    def biome_palette(self):
        return self.__biome_palette


class Biome2DChunk:
    def __init__(
        self,
        array_shape: tuple[int, int],
        array: Union[int, ArrayLike],
    ):
        if (
            not isinstance(array_shape, tuple)
            and len(array_shape) == 2
            and all(isinstance(s, int) for s in array_shape)
        ):
            raise TypeError

        self.__array_shape = array_shape
        self.__biome_palette = BiomePalette()
        self.biome = array

    @property
    def biome(self) -> numpy.ndarray:
        return self.__biomes

    @biome.setter
    def biome(
        self,
        array: Union[int, ArrayLike],
    ):
        if isinstance(array, int):
            self.__biomes = numpy.full(self.__array_shape, array, dtype=numpy.uint32)
        else:
            array = numpy.asarray(array)
            if not isinstance(array, numpy.ndarray):
                raise TypeError
            if array.shape != self.__array_shape or array.dtype != numpy.uint32:
                raise ValueError
            self.__biomes = numpy.array(array)

    @property
    def biome_palette(self):
        return self.__biome_palette
