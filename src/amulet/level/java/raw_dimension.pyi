from __future__ import annotations

import typing

import amulet.biome
import amulet.block
import amulet.level.java.chunk
import amulet.selection.box
import amulet.utils.lock
import amulet_nbt

__all__ = ["JavaRawDimension"]

class JavaRawDimension:
    def compact(self) -> None:
        """
        Compact the level.
        External shared read lock required.
        """

    def decode_chunk(
        self, raw_chunk: dict[str, amulet_nbt.NamedTag], cx: int, cz: int
    ) -> amulet.level.java.chunk.JavaChunk:
        """
        Decode a raw chunk to a chunk object.
        TODO: thread safety
        """

    def delete_chunk(self, cx: int, cz: int) -> None:
        """
        Delete the chunk from this dimension.
        External shared read-write lock required.
        """

    def encode_chunk(
        self, chunk: amulet.level.java.chunk.JavaChunk, cx: int, cz: int
    ) -> dict[str, amulet_nbt.NamedTag]:
        """
        Encode a chunk object to its raw data.
        TODO: thread safety
        """

    def get_raw_chunk(self, cx: int, cz: int) -> dict[str, amulet_nbt.NamedTag]:
        """
        Get the raw chunk from this dimension.
        External shared read lock required.
        """

    def has_chunk(self, cx: int, cz: int) -> bool:
        """
        Does the chunk exist in this dimension.
        External shared read lock required.
        External shared read-only lock optional.
        """

    def set_raw_chunk(
        self, cx: int, cz: int, chunk: dict[str, amulet_nbt.NamedTag]
    ) -> None:
        """
        Set the chunk in this dimension from raw data.
        External shared read-write lock required.
        """

    @property
    def all_chunk_coords(self) -> typing.Iterator[tuple[int, int]]:
        """
        An iterator of all chunk coordinates in the dimension.
        External shared read lock required.
        External shared read-only lock optional.
        """

    @property
    def bounds(self) -> amulet.selection.box.SelectionBox:
        """
        The selection box that fills the whole world.
        Thread safe.
        """

    @property
    def default_biome(self) -> amulet.biome.Biome:
        """
        The default biome for this dimension.
        Thread safe.
        """

    @property
    def default_block(self) -> amulet.block.BlockStack:
        """
        The default block for this dimension.
        Thread safe.
        """

    @property
    def dimension_id(self) -> str:
        """
        The identifier for this dimension. eg. "minecraft:overworld".
        Thread safe.
        """

    @property
    def lock(self) -> amulet.utils.lock.OrderedLock:
        """
        The public lock
        Thread safe.
        """

    @property
    def relative_path(self) -> str:
        """
        The relative path to the dimension. eg. "DIM1".
        Thread safe.
        """
