from ._region import AnvilRegion as AnvilRegion
from _typeshed import Incomplete
from amulet.api.data_types import ChunkCoordinates as ChunkCoordinates, RegionCoordinates as RegionCoordinates
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist
from amulet.utils import world_utils as world_utils
from amulet_nbt import NamedTag
from typing import Dict, Iterable

InternalDimension = str
ChunkDataType = Dict[str, NamedTag]

class AnvilDimensionManager:
    """
    A class to manage the data for a dimension.
    This can consist of multiple layers. Eg the region layer which contains chunk data and the entities layer which contains entities.
    """
    level_regex: Incomplete
    _directory: Incomplete
    _mcc: Incomplete
    __layers: Incomplete
    __default_layer: Incomplete
    def __init__(self, directory: str, *, mcc: bool = ..., layers=...) -> None: ...
    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def unload(self) -> None: ...
    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
    def get_chunk_data_layers(self, cx: int, cz: int) -> ChunkDataType:
        """Get the chunk data for each layer"""
    def put_chunk_data(self, cx: int, cz: int, data: NamedTag):
        """pass data to the region file class"""
    def put_chunk_data_layers(self, cx: int, cz: int, data_layers: ChunkDataType):
        """Put one or more layers of data"""
    def delete_chunk(self, cx: int, cz: int): ...

class AnvilRegionManager:
    """A class to manage a directory of region files."""
    _directory: Incomplete
    _regions: Incomplete
    _mcc: Incomplete
    _lock: Incomplete
    def __init__(self, directory: str, *, mcc: bool = ...) -> None: ...
    def unload(self) -> None: ...
    def _region_path(self, rx, rz) -> str:
        """Get the file path for a region file."""
    def _has_region(self, rx: int, rz: int) -> bool:
        """Does a region file exist."""
    def _get_region(self, rx: int, rz: int, create: bool = ...) -> AnvilRegion: ...
    def _iter_regions(self) -> Iterable[AnvilRegion]: ...
    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
    def put_chunk_data(self, cx: int, cz: int, data: NamedTag):
        """pass data to the region file class"""
    def delete_chunk(self, cx: int, cz: int): ...
