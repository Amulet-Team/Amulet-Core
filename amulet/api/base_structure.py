from __future__ import annotations

from typing import Union, Generator, Dict, Optional, Tuple

from .block import Block
from .chunk import Chunk
from .selection import SelectionBox
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
        self, *args, **kwargs
    ) -> Generator[Tuple[Chunk, SelectionBox], None, None]:
        raise NotImplementedError

    def get_chunk_slices(
        self, *args, **kwargs
    ) -> Generator[Tuple[Chunk, Tuple[slice, slice, slice], SelectionBox], None, None]:
        raise NotImplementedError
