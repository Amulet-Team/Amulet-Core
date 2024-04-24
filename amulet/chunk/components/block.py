from __future__ import annotations

from typing import Union, Iterable
from collections.abc import Mapping

from numpy.typing import ArrayLike

from amulet.version import VersionRange
from amulet.palette import BlockPalette
from amulet.block import BlockStack
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer
from amulet.utils.typed_property import TypedProperty

from .abc import ChunkComponent, UnloadedComponent


class BlockComponentData:
    def __init__(
        self,
        version_range: VersionRange,
        array_shape: tuple[int, int, int],
        default_array: Union[int, ArrayLike],
        default_block: BlockStack,
    ):
        self._palette = BlockPalette(version_range)
        self._palette.block_stack_to_index(default_block)
        self._sections = SubChunkArrayContainer(array_shape, default_array)

    @TypedProperty[
        SubChunkArrayContainer,
        Mapping[int, ArrayLike] | Iterable[tuple[int, ArrayLike]],
    ]
    def sections(self) -> SubChunkArrayContainer:
        return self._sections

    @sections.setter
    def _set_block(
        self,
        sections: Mapping[int, ArrayLike] | Iterable[tuple[int, ArrayLike]],
    ) -> None:
        self._sections = SubChunkArrayContainer(
            self._sections.array_shape, self._sections.default_array, sections
        )

    @property
    def palette(self) -> BlockPalette:
        return self._palette


class BlockComponent(ChunkComponent[BlockComponentData, BlockComponentData]):
    storage_key = b"bl"

    @staticmethod
    def fix_set_data(old_obj: BlockComponentData | UnloadedComponent, new_obj: BlockComponentData) -> BlockComponentData:
        if not isinstance(new_obj, BlockComponentData):
            raise TypeError
        assert isinstance(old_obj, BlockComponentData)
        if old_obj.sections.array_shape != new_obj.sections.array_shape:
            raise ValueError("New array shape does not match old array shape.")
        elif old_obj.palette.version_range != new_obj.palette.version_range:
            raise ValueError("New version range does not match old version range.")
        return new_obj
