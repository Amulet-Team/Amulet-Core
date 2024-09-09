from __future__ import annotations

import os as os
import re as re
import threading as threading
import types
import typing
from collections.abc import Iterator, Sequence

from amulet.errors import ChunkDoesNotExist
from amulet.level.java.anvil._region import AnvilRegion
from amulet.utils import world_utils
from amulet_nbt import NamedTag

__all__ = [
    "AnvilDimension",
    "AnvilDimensionLayer",
    "AnvilRegion",
    "ChunkCoordinates",
    "ChunkDoesNotExist",
    "Iterator",
    "NamedTag",
    "RawChunkType",
    "RegionCoordinates",
    "Sequence",
    "os",
    "re",
    "threading",
    "world_utils",
]

class AnvilDimension:
    """

    A class to manage the data for a dimension.
    This can consist of multiple layers. Eg the region layer which contains chunk data and the entities layer which contains entities.

    """

    level_regex: typing.ClassVar[
        re.Pattern
    ]  # value = re.compile('DIM(?P<level>-?\\d+)')
    def __init__(
        self,
        directory: str,
        *,
        mcc: bool = False,
        layers: typing.Sequence[str] = ("region"),
    ) -> None: ...
    def all_chunk_coords(self) -> typing.Iterator[ChunkCoordinates]: ...
    def compact(self) -> None:
        """
        Compact all region files in this dimension
        """

    def delete_chunk(self, cx: int, cz: int) -> None: ...
    def get_chunk_data(self, cx: int, cz: int) -> RawChunkType:
        """
        Get the chunk data for each layer
        """

    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def put_chunk_data(self, cx: int, cz: int, data_layers: RawChunkType) -> None:
        """
        Put one or more layers of data
        """

class AnvilDimensionLayer:
    """
    A class to manage a directory of region files.
    """

    def __init__(self, directory: str, *, mcc: bool = False): ...
    def _get_region(self, rx: int, rz: int, create: bool = False) -> AnvilRegion: ...
    def _has_region(self, rx: int, rz: int) -> bool:
        """
        Does a region file exist.
        """

    def _iter_regions(self) -> typing.Iterator[AnvilRegion]: ...
    def _region_path(self, rx: int, rz: int) -> str:
        """
        Get the file path for a region file.
        """

    def all_chunk_coords(self) -> typing.Iterator[ChunkCoordinates]: ...
    def compact(self) -> None:
        """
        Compact all region files in this layer
        """

    def delete_chunk(self, cx: int, cz: int) -> None: ...
    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """

        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist

        """

    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def put_chunk_data(self, cx: int, cz: int, data: NamedTag) -> None:
        """
        pass data to the region file class
        """

ChunkCoordinates: types.GenericAlias  # value = tuple[int, int]
RawChunkType: types.GenericAlias  # value = dict[str, amulet_nbt.NamedTag]
RegionCoordinates: types.GenericAlias  # value = tuple[int, int]
