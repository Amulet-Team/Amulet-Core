from __future__ import annotations

from typing import Union, Iterable
from collections.abc import Mapping

import numpy
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
        default_block: BlockStack,
    ):
        self._palette = BlockPalette(version_range)
        self._palette.block_stack_to_index(default_block)
        self._sections = SubChunkArrayContainer(array_shape, 0)

    @TypedProperty[
        SubChunkArrayContainer,
        SubChunkArrayContainer
        | Mapping[int, numpy.ndarray]
        | Iterable[tuple[int, numpy.ndarray]],
    ]
    def sections(self) -> SubChunkArrayContainer:
        return self._sections

    @sections.setter
    def _set_block(
        self,
        sections: (
            SubChunkArrayContainer
            | Mapping[int, numpy.ndarray]
            | Iterable[tuple[int, numpy.ndarray]]
        ),
    ) -> None:
        if sections is not self._sections:
            self._sections.clear()
            self._sections.update(sections)
            if isinstance(sections, SubChunkArrayContainer):
                self._sections.default_array = sections.default_array

    @property
    def palette(self) -> BlockPalette:
        return self._palette


class BlockComponent(ChunkComponent[BlockComponentData, BlockComponentData]):
    storage_key = b"bl"

    @staticmethod
    def fix_set_data(
        old_obj: BlockComponentData | UnloadedComponent, new_obj: BlockComponentData
    ) -> BlockComponentData:
        if not isinstance(new_obj, BlockComponentData):
            raise TypeError
        assert isinstance(old_obj, BlockComponentData)
        if old_obj.sections.array_shape != new_obj.sections.array_shape:
            raise ValueError("New array shape does not match old array shape.")
        elif old_obj.palette.version_range != new_obj.palette.version_range:
            raise ValueError("New version range does not match old version range.")
        return new_obj