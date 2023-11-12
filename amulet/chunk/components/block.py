from typing import Union, Iterable

from numpy.typing import ArrayLike

from amulet.version import VersionRange
from amulet.palette import BlockPalette
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer
from amulet.utils.typed_property import TypedProperty


class BlockComponent:
    def __init__(
        self,
        version_range: VersionRange,
        array_shape: tuple[int, int, int],
        default_array: Union[int, ArrayLike],
    ):
        self.__block_palette = BlockPalette(version_range)
        self.__blocks = SubChunkArrayContainer(array_shape, default_array)

    @TypedProperty[SubChunkArrayContainer, Iterable[tuple[int, ArrayLike]]]
    def block(self) -> SubChunkArrayContainer:
        return self.__blocks

    @block.setter
    def _set_block(
        self,
        sections: Iterable[tuple[int, ArrayLike]],
    ) -> None:
        self.__blocks = SubChunkArrayContainer(
            self.__blocks.array_shape, self.__blocks.default_array, sections
        )

    @property
    def block_palette(self) -> BlockPalette:
        return self.__block_palette
