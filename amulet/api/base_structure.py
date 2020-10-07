from __future__ import annotations

from typing import Union, Generator, Optional, Tuple

from .block import Block
from .chunk import Chunk
from .selection import SelectionBox, SelectionGroup
from .data_types import Dimension


class BaseStructure:
    @property
    def sub_chunk_size(self) -> int:
        return 16

    @property
    def chunk_size(self) -> Tuple[int, int, int]:
        return self.sub_chunk_size, self.sub_chunk_size * 16, self.sub_chunk_size

    def get_chunk(self, cx: int, cz: int, dimension: Optional[Dimension]) -> Chunk:
        """
        Gets the chunk data of the specified chunk coordinates.
        If the chunk does not exist ChunkDoesNotExist is raised.
        If some other error occurs then ChunkLoadError is raised (this error will also catch ChunkDoesNotExist)

        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :param dimension: The dimension to get the chunk from
        :return: A Chunk object containing the data for the chunk
        :raises: `amulet.api.errors.ChunkDoesNotExist` if the chunk does not exist or `amulet.api.errors.ChunkLoadError` if the chunk failed to load for some reason. (This also includes it not existing)
        """
        raise NotImplementedError

    def get_block(self, x: int, y: int, z: int, dimension: Optional[Dimension]) -> Block:
        """
        Gets the universal Block object at the specified coordinates

        :param x: The X coordinate of the desired block
        :param y: The Y coordinate of the desired block
        :param z: The Z coordinate of the desired block
        :param dimension: The dimension of the desired block
        :return: The universal Block object representation of the block at that location
        :raise: Raises ChunkDoesNotExist or ChunkLoadError if the chunk was not loaded.
        """
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
            dimension: Optional[Dimension],
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
            dimension: Optional[Dimension],
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
