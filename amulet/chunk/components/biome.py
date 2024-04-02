from typing import Union, Iterable
from collections.abc import Mapping

import numpy
from numpy.typing import ArrayLike

from amulet.version import VersionRange
from amulet.palette import BiomePalette
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer
from amulet.utils.typed_property import TypedProperty


class Biome3DComponent:
    def __init__(
        self,
        version_range: VersionRange,
        array_shape: tuple[int, int, int],
        default_array: Union[int, ArrayLike],
    ):
        self.__biome_palette = BiomePalette(version_range)
        self.__biomes = SubChunkArrayContainer(array_shape, default_array)

    @TypedProperty[
        SubChunkArrayContainer,
        Mapping[int, ArrayLike] | Iterable[tuple[int, ArrayLike]],
    ]
    def biomes(self) -> SubChunkArrayContainer:
        return self.__biomes

    @biomes.setter
    def _set_biome(
        self,
        sections: Mapping[int, ArrayLike] | Iterable[tuple[int, ArrayLike]],
    ) -> None:
        self.__biomes = SubChunkArrayContainer(
            self.__biomes.array_shape, self.__biomes.default_array, sections
        )

    @property
    def biome_palette(self) -> BiomePalette:
        return self.__biome_palette


class Biome2DComponent:
    __biomes: numpy.ndarray

    def __init__(
        self,
        version_range: VersionRange,
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
        self.__biome_palette = BiomePalette(version_range)
        self._set_biome(array)

    @TypedProperty[numpy.ndarray, Union[int, ArrayLike]]
    def biomes(self) -> numpy.ndarray:
        return self.__biomes

    @biomes.setter
    def _set_biome(
        self,
        array: Union[int, ArrayLike],
    ) -> None:
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
    def biome_palette(self) -> BiomePalette:
        return self.__biome_palette
