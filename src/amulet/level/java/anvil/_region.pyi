from collections.abc import Iterator
from enum import IntEnum

from _typeshed import Incomplete
from amulet.data_types import ChunkCoordinates as ChunkCoordinates
from amulet.errors import ChunkDoesNotExist as ChunkDoesNotExist
from amulet.errors import ChunkLoadError as ChunkLoadError
from amulet_nbt import NamedTag as NamedTag

from ._sector_manager import Sector as Sector
from ._sector_manager import SectorManager as SectorManager

SectorSize: int
MaxRegionSize: Incomplete
HeaderSector: Incomplete
log: Incomplete

class RegionFileVersion(IntEnum):
    VERSION_GZIP: int
    VERSION_DEFLATE: int
    VERSION_NONE: int
    VERSION_LZ4: int

LZ4_HEADER: Incomplete
LZ4_MAGIC: bytes
COMPRESSION_METHOD_RAW: int
COMPRESSION_METHOD_LZ4: int

class AnvilRegion:
    """
    A class to read and write Minecraft Java Edition Region files.
    Only one class should exist per region file at any given time otherwise bad things may happen.
    """

    region_regex: Incomplete
    @classmethod
    def get_coords(cls, file_path: str) -> tuple[int, int]:
        """Parse a region file path to get the region coordinates."""

    def __init__(self, file_path: str, *, mcc: bool = False) -> None:
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

    def get_mcc_path(self, cx: int, cz: int) -> str:
        """Get the mcc path. Coordinates are world chunk coordinates."""

    def all_coords(self) -> Iterator[ChunkCoordinates]:
        """An iterable of chunk coordinates in world space."""

    def has_data(self, cx: int, cz: int) -> bool:
        """Does the chunk exists. Coords are in world space."""

    def get_data(self, cx: int, cz: int) -> NamedTag: ...
    def set_data(self, cx: int, cz: int, data: NamedTag) -> None:
        """Write the data to the region file."""

    def delete_data(self, cx: int, cz: int) -> None:
        """Delete the data from the region file."""

    def compact(self) -> None:
        """Compact the region file.
        This moves all entries to the front of the file and deletes any unused space."""
