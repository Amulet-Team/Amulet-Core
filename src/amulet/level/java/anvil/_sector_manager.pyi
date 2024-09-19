from __future__ import annotations

import threading as threading
import typing
from typing import NamedTuple

from _bisect import bisect_left, bisect_right

__all__ = [
    "NamedTuple",
    "NoValidSector",
    "Sector",
    "SectorManager",
    "bisect_left",
    "bisect_right",
    "threading",
]

class NoValidSector(Exception):
    """
    An error for when there is no sector large enough and the region cannot be resized.
    """

class Sector(tuple):
    """
    Sector(start, stop)
    """

    __slots__: typing.ClassVar[tuple] = tuple()
    _field_defaults: typing.ClassVar[dict] = {}
    _fields: typing.ClassVar[tuple] = ("start", "stop")
    @staticmethod
    def __new__(_cls, start: ForwardRef("int"), stop: ForwardRef("int")):
        """
        Create new instance of Sector(start, stop)
        """

    @classmethod
    def _make(cls, iterable):
        """
        Make a new Sector object from a sequence or iterable
        """

    def __getnewargs__(self):
        """
        Return self as a plain tuple.  Used by copy and pickle.
        """

    def __repr__(self):
        """
        Return a nicely formatted representation string
        """

    def _asdict(self):
        """
        Return a new dict which maps field names to their values.
        """

    def _replace(self, **kwds):
        """
        Return a new Sector object replacing specified fields with new values
        """

    def contains(self, other: Sector) -> bool:
        """
        Is the other sector entirely within this sector.
        """

    def intersects(self, other: Sector) -> bool:
        """
        Do the two sectors intersect each other.
        """

    def neighbours(self, other: Sector) -> bool:
        """
        Do the two sectors neighbour but not intersect.
        """

    def split(self, other: Sector) -> list[Sector]:
        """

        Split this sector around another sector.
        The other sector must be contained within this sector

        :param other: The other sector to split around.
        :return: A list of 0-2 sectors

        """

    @property
    def length(self) -> int: ...

class SectorManager:
    """
    A class to manage a sequence of memory.
    """

    def __init__(self, start: int, stop: int, resizable: bool = True):
        """

        :param start: The start of the memory region
        :param stop: The end of the memory region
        :param resizable: Can the region be resized

        """

    def _add_size_sector(self, sector: Sector) -> None: ...
    def free(self, sector: Sector) -> None:
        """

        Free a reserved sector.
        The sector must match exactly a sector previously reserved.

        :param sector: The sector to free

        """

    def reserve(self, sector: Sector) -> None:
        """

        Mark a section as reserved.
        If you don't know exactly where the sector is use `reserve_space` to find and reserve a new sector

        :param sector: The sector to reserve

        """

    def reserve_space(self, length: int) -> Sector:
        """

        Find and reserve a memory location large enough to fit the requested memory.

        :param length: The length of the memory region to reserve
        :return: The index of the start of the reserved memory region

        """

    @property
    def sectors(self) -> list[Sector]:
        """
        A list of reserved sectors. Ordered by their start location.
        """
