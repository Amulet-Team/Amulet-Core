from _typeshed import Incomplete
from typing import List, NamedTuple

class NoValidSector(Exception):
    """An error for when there is no sector large enough and the region cannot be resized."""

class Sector(NamedTuple):
    start: int
    stop: int
    @property
    def length(self) -> int: ...
    def intersects(self, other: Sector):
        """Do the two sectors intersect each other."""
    def contains(self, other: Sector):
        """Is the other sector entirely within this sector."""
    def neighbours(self, other: Sector):
        """Do the two sectors neighbour but not intersect."""
    def split(self, other: Sector) -> List[Sector]:
        """
        Split this sector around another sector.
        The other sector must be contained within this sector

        :param other: The other sector to split around.
        :return: A list of 0-2 sectors
        """

class SectorManager:
    """A class to manage a sequence of memory."""
    _lock: Incomplete
    _stop: Incomplete
    _resizable: Incomplete
    _free_start: Incomplete
    _free_size: Incomplete
    _reserved: Incomplete
    def __init__(self, start: int, stop: int, resizable: bool = ...) -> None:
        """
        :param start: The start of the memory region
        :param stop: The end of the memory region
        :param resizable: Can the region be resized
        """
    @property
    def sectors(self) -> List[Sector]:
        """A list of reserved sectors. Ordered by their start location."""
    def reserve_space(self, length: int) -> Sector:
        """
        Find and reserve a memory location large enough to fit the requested memory.

        :param length: The length of the memory region to reserve
        :return: The index of the start of the reserved memory region
        """
    def reserve(self, sector: Sector):
        """
        Mark a section as reserved.
        If you don't know exactly where the sector is use `reserve_space` to find and reserve a new sector

        :param sector: The sector to reserve
        """
    def _add_size_sector(self, sector: Sector): ...
    def free(self, sector: Sector):
        """
        Free a reserved sector.
        The sector must match exactly a sector previously reserved.

        :param sector: The sector to free
        """
