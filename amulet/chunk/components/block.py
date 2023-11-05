from typing import Union, Iterable

from numpy.typing import ArrayLike

from amulet.version import VersionRange
from amulet.palette import BlockPalette
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer


class BlockComponent:
    def __init__(
        self,
        version_range: VersionRange,
        array_shape: tuple[int, int, int],
        default_array: Union[int, ArrayLike],
    ):
        self.__block_palette = BlockPalette(version_range)
        self.__blocks = SubChunkArrayContainer(array_shape, default_array)

    @property
    def block(self) -> SubChunkArrayContainer:
        return self.__blocks

    @block.setter
    def block(
        self,
        sections: Iterable[int, ArrayLike],
    ):
        self.__blocks = SubChunkArrayContainer(
            self.__blocks.array_shape, self.__blocks.default_array, sections
        )

    @property
    def block_palette(self):
        return self.__block_palette
