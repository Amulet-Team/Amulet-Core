from collections.abc import Iterator, Sequence
from typing import TypeAlias

from _typeshed import Incomplete
from amulet.data_types import ChunkCoordinates as ChunkCoordinates
from amulet.data_types import RegionCoordinates as RegionCoordinates
from amulet.errors import ChunkDoesNotExist as ChunkDoesNotExist
from amulet.utils import world_utils as world_utils
from amulet_nbt import NamedTag

from ._region import AnvilRegion as AnvilRegion

RawChunkType: TypeAlias

class AnvilDimensionLayer:
    """A class to manage a directory of region files."""

    def __init__(self, directory: str, *, mcc: bool = False) -> None: ...
    def all_chunk_coords(self) -> Iterator[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """

    def put_chunk_data(self, cx: int, cz: int, data: NamedTag) -> None:
        """pass data to the region file class"""

    def delete_chunk(self, cx: int, cz: int) -> None: ...
    def compact(self) -> None:
        """Compact all region files in this layer"""

class AnvilDimension:
    """
    A class to manage the data for a dimension.
    This can consist of multiple layers. Eg the region layer which contains chunk data and the entities layer which contains entities.
    """

    level_regex: Incomplete
    def __init__(
        self, directory: str, *, mcc: bool = False, layers: Sequence[str] = ("region",)
    ) -> None: ...
    def all_chunk_coords(self) -> Iterator[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def get_chunk_data(self, cx: int, cz: int) -> RawChunkType:
        """Get the chunk data for each layer"""

    def put_chunk_data(self, cx: int, cz: int, data_layers: RawChunkType) -> None:
        """Put one or more layers of data"""

    def delete_chunk(self, cx: int, cz: int) -> None: ...
    def compact(self) -> None:
        """Compact all region files in this dimension"""
