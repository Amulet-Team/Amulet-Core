import threading
from ._sector_manager import Sector as Sector, SectorManager as SectorManager
from _typeshed import Incomplete
from amulet.api.data_types import ChunkCoordinates as ChunkCoordinates
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ChunkLoadError as ChunkLoadError
from amulet_nbt import NamedTag as NamedTag
from enum import IntEnum
from typing import BinaryIO, Dict, Generator, Optional, Tuple, Union

Depreciated: Incomplete
SectorSize: int
MaxRegionSize: Incomplete
log: Incomplete

class RegionFileVersion(IntEnum):
    VERSION_GZIP: int
    VERSION_DEFLATE: int
    VERSION_NONE: int

def _validate_region_coords(cx: int, cz: int):
    """Make sure that the coordinates are in region space."""
def _compress(data: NamedTag) -> bytes:
    """Convert an NBTFile into a compressed bytes object"""
def _decompress(data: bytes) -> NamedTag:
    """Convert a bytes object into an NBTFile"""
def _sanitise_file(handler: BinaryIO): ...

class AnvilRegion:
    """
    A class to read and write Minecraft Java Edition Region files.
    Only one class should exist per region file at any given time otherwise bad things may happen.
    """
    region_regex: Incomplete
    __slots__: Incomplete
    _path: str
    _rx: int
    _rz: int
    _mcc: bool
    _sector_manager: Optional[SectorManager]
    _chunk_locations: Dict[ChunkCoordinates, Sector]
    _lock: threading.RLock
    @classmethod
    def get_coords(cls, file_path: str) -> Union[Tuple[None, None], Tuple[int, int]]:
        """Parse a region file path to get the region coordinates."""
    def __init__(self, file_path: str, create=..., mcc: bool = ...) -> None:
        """
        A class wrapper for a region file
        :param file_path: The file path of the region file
        :param create: bool - if true will create the region from scratch. If false will try loading from disk
        """
    @property
    def path(self) -> str:
        """The file path to the region file."""
    @property
    def rx(self) -> int:
        """The region x coordinate."""
    @property
    def rz(self) -> int:
        """The region z coordinate."""
    def get_mcc_path(self, cx: int, cz: int):
        """Get the mcc path. Coordinates are global chunk coordinates."""
    def _load(self) -> None: ...
    def all_chunk_coords(self) -> Generator[ChunkCoordinates, None, None]:
        """An iterable of chunk coordinates in world space."""
    def has_chunk(self, cx: int, cz: int) -> bool:
        """Does the chunk exists. Coords are in region space."""
    def unload(self) -> None:
        """Unload the data if it is not being used."""
    def get_data(self, cx: int, cz: int) -> NamedTag: ...
    def _write_data(self, cx: int, cz: int, data: Optional[bytes]): ...
    def write_data(self, cx: int, cz: int, data: NamedTag):
        """Write the data to the region file."""
    def delete_data(self, cx: int, cz: int):
        """Delete the data from the region file."""
