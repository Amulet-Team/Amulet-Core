from __future__ import annotations

from typing import Union, Generator, Dict, Optional, Tuple

from .block import Block
from .chunk import Chunk
from .selection import SelectionBox, SelectionGroup
from .data_types import DimensionCoordinates

ChunkCache = Dict[DimensionCoordinates, Optional[Chunk]]


class BaseStructure:
    @property
    def sub_chunk_size(self) -> int:
        return 16

    @property
    def chunk_size(self) -> Tuple[int, int, int]:
        return self.sub_chunk_size, self.sub_chunk_size * 16, self.sub_chunk_size

    def get_chunk(self, *args, **kwargs) -> Chunk:
        raise NotImplementedError

    def get_block(self, *args, **kwargs) -> Block:
        raise NotImplementedError

    def _chunk_box(
            self,
            cx: int,
            cz: int,
            chunk_size: Optional[Tuple[int, Union[int, None], int]] = None,
    ):
        """Get a SelectionBox containing the whole of a given chunk"""
        if chunk_size is None:
            chunk_size = self.chunk_size
        return SelectionBox.create_chunk_box(cx, cz, chunk_size[0])

    def get_chunk_boxes(
            self,
            selection: Union[SelectionGroup, SelectionBox, None],
            dimension: Optional[str],
            create_missing_chunks: bool = False
    ) -> Generator[Tuple[Chunk, SelectionBox], None, None]:
        """Given a selection will yield chunks and `SelectionBox`es into that chunk

        :param selection: SelectionGroup or SelectionBox into the world
        :param dimension: The dimension to take effect in
        :param create_missing_chunks: If a chunk does not exist an empty one will be created (defaults to false)
        """
        raise NotImplementedError

    def get_chunk_slices(
            self,
            selection: Union[SelectionGroup, SelectionBox, None],
            dimension: Optional[str],
            create_missing_chunks: bool = False
    ) -> Generator[Tuple[Chunk, Tuple[slice, slice, slice], SelectionBox], None, None]:
        """Given a selection will yield chunks, slices into that chunk and the corresponding box

        :param selection: SelectionGroup or SelectionBox into the world
        :param dimension: The dimension to take effect in
        :param create_missing_chunks: If a chunk does not exist an empty one will be created (defaults to false)
        Usage:
        for chunk, slice, box in world.get_chunk_slices(selection):
            chunk.blocks[slice] = ...
        """
        raise NotImplementedError
