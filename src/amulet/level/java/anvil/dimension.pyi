from __future__ import annotations

import collections.abc
import typing

import amulet.level.java.anvil.region
import amulet_nbt

__all__ = ["AnvilDimension", "AnvilDimensionLayer", "RawChunkType"]

class AnvilDimension:
    """
    A class to manage the data for a dimension.
    This can consist of multiple layers. Eg the region layer which contains chunk data and the entities layer which contains entities.
    """

    def __init__(
        self,
        directory: str,
        layer_names: collections.abc.Iterable[str],
        mcc: bool = False,
    ) -> None: ...
    def all_chunk_coords(self) -> typing.Iterator[tuple[int, int]]:
        """
        Get an iterator for all the chunks that exist in this dimension.
        """

    def compact(self) -> None:
        """
        Defragment the region files and remove unused region files.
        """

    def delete_chunk(self, cx: int, cz: int) -> None:
        """
        Delete all data for the given chunk.
        """

    def get_chunk_data(self, cx: int, cz: int) -> dict[str, amulet_nbt.NamedTag]:
        """
        Get the data for a chunk
        """

    def get_layer(self, layer_name: str) -> AnvilDimensionLayer:
        """
        Get the AnvilDimensionLayer for a specific layer. The returned value must not be stored long-term.
        """

    def has_chunk(self, cx: int, cz: int) -> bool:
        """
        Check if a chunk exists.
        """

    def has_layer(self, layer_name: str) -> bool:
        """
        Check if this dimension has the requested layer.
        """

    def set_chunk_data(
        self,
        cx: int,
        cz: int,
        data_layers: collections.abc.Iterable[tuple[str, amulet_nbt.NamedTag]],
    ) -> None:
        """
        Set the data for a chunk.
        """

class AnvilDimensionLayer:
    """
    A class to manage a directory of region files.
    """

    def __init__(self, directory: str, mcc: bool = False) -> None: ...
    def all_chunk_coords(self) -> typing.Iterator[tuple[int, int]]:
        """
        An iterator of all chunk coordinates in this layer.
        """

    def all_region_coords(self) -> typing.Iterator[tuple[int, int]]:
        """
        An iterator of all region coordinates in this layer.
        """

    def compact(self) -> None:
        """
        Defragment the region files and remove unused region files.
        """

    def delete_chunk(self, cx: int, cz: int) -> None:
        """
        Delete the chunk data from this layer.
        """

    def get_chunk_data(self, cx: int, cz: int) -> amulet_nbt.NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """

    def get_region(
        self, rx: int, rz: int, create: bool = False
    ) -> amulet.level.java.anvil.region.AnvilRegion:
        """
        Get an AnvilRegion instance. This must not be stored long-term.
        """

    def has_chunk(self, cx: int, cz: int) -> bool:
        """
        Check if the chunk has data in this layer.
        """

    def has_region(self, rx: int, rz: int) -> bool:
        """
        Check if a region file exists in this layer.
        """

    def set_chunk_data(self, cx: int, cz: int, tag: amulet_nbt.NamedTag) -> None:
        """
        Set the chunk data for this layer.
        """

    @property
    def directory(self) -> str:
        """
        The directory this instance manages.
        """

    @property
    def mcc(self) -> bool:
        """
        Is mcc file support enabled for this instance.
        """

RawChunkType: typing.TypeAlias = dict[str, amulet_nbt.NamedTag]
