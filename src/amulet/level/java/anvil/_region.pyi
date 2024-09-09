from __future__ import annotations

import enum
import gzip as gzip
import logging as logging
import os as os
import re as re
import struct as struct
import threading as threading
import time as time
import types
import typing
import zlib as zlib
from collections.abc import Iterator
from enum import IntEnum
from typing import BinaryIO

import _struct
import amulet.level.java.anvil._sector_manager
import numpy as numpy
from amulet.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.level.java.anvil._sector_manager import Sector, SectorManager
from amulet_nbt import NamedTag, read_nbt
from lz4 import block as lz4_block

__all__ = [
    "AnvilRegion",
    "BinaryIO",
    "COMPRESSION_METHOD_LZ4",
    "COMPRESSION_METHOD_RAW",
    "ChunkCoordinates",
    "ChunkDoesNotExist",
    "ChunkLoadError",
    "HeaderSector",
    "IntEnum",
    "Iterator",
    "LZ4_HEADER",
    "LZ4_MAGIC",
    "MaxRegionSize",
    "NamedTag",
    "RegionFileVersion",
    "Sector",
    "SectorManager",
    "SectorSize",
    "gzip",
    "log",
    "logging",
    "lz4_block",
    "numpy",
    "os",
    "re",
    "read_nbt",
    "struct",
    "threading",
    "time",
    "zlib",
]

class AnvilRegion:
    """

    A class to read and write Minecraft Java Edition Region files.
    Only one class should exist per region file at any given time otherwise bad things may happen.

    """

    __slots__: typing.ClassVar[tuple] = (
        "_path",
        "_rx",
        "_rz",
        "_mcc",
        "_sector_manager",
        "_chunk_locations",
        "_lock",
    )
    region_regex: typing.ClassVar[
        re.Pattern
    ]  # value = re.compile('r\\.(?P<rx>-?\\d+)\\.(?P<rz>-?\\d+)\\.mca')
    @classmethod
    def get_coords(cls, file_path: str) -> tuple[int, int]:
        """
        Parse a region file path to get the region coordinates.
        """

    def __init__(self, file_path: str, *, mcc: bool = False) -> None:
        """

        A class wrapper for a region file
        :param file_path: The file path of the region file
        :param create: bool - if true will create the region from scratch. If false will try loading from disk

        """

    def _load(self) -> None:
        """
        Load region metadata. The lock must be acquired when calling this.
        """

    def _write_data(self, cx: int, cz: int, data: bytes | None) -> None: ...
    def all_coords(self) -> typing.Iterator[ChunkCoordinates]:
        """
        An iterable of chunk coordinates in world space.
        """

    def compact(self) -> None:
        """
        Compact the region file.
                This moves all entries to the front of the file and deletes any unused space.
        """

    def delete_data(self, cx: int, cz: int) -> None:
        """
        Delete the data from the region file.
        """

    def get_data(self, cx: int, cz: int) -> NamedTag: ...
    def get_mcc_path(self, cx: int, cz: int) -> str:
        """
        Get the mcc path. Coordinates are world chunk coordinates.
        """

    def has_data(self, cx: int, cz: int) -> bool:
        """
        Does the chunk exists. Coords are in world space.
        """

    def set_data(self, cx: int, cz: int, data: NamedTag) -> None:
        """
        Write the data to the region file.
        """

    @property
    def path(self) -> str:
        """
        The file path to the region file.
        """

    @property
    def rx(self) -> int:
        """
        The region x coordinate.
        """

    @property
    def rz(self) -> int:
        """
        The region z coordinate.
        """

class RegionFileVersion(enum.IntEnum):
    VERSION_DEFLATE: typing.ClassVar[
        RegionFileVersion
    ]  # value = <RegionFileVersion.VERSION_DEFLATE: 2>
    VERSION_GZIP: typing.ClassVar[
        RegionFileVersion
    ]  # value = <RegionFileVersion.VERSION_GZIP: 1>
    VERSION_LZ4: typing.ClassVar[
        RegionFileVersion
    ]  # value = <RegionFileVersion.VERSION_LZ4: 4>
    VERSION_NONE: typing.ClassVar[
        RegionFileVersion
    ]  # value = <RegionFileVersion.VERSION_NONE: 3>
    @classmethod
    def __new__(cls, value): ...
    def __format__(self, format_spec):
        """
        Convert to a string according to format_spec.
        """

def _compress(tag: NamedTag) -> bytes:
    """
    Convert an NBTFile into a compressed bytes object
    """

def _decompress(data: bytes) -> NamedTag:
    """
    Convert a bytes object into an NBTFile
    """

def _decompress_lz4(data: bytes) -> bytes:
    """
    The LZ4 compression format is a sequence of LZ4 blocks with some header data.
    """

def _sanitise_file(handler: BinaryIO) -> None: ...

COMPRESSION_METHOD_LZ4: int = 32
COMPRESSION_METHOD_RAW: int = 16
ChunkCoordinates: types.GenericAlias  # value = tuple[int, int]
HeaderSector: (
    amulet.level.java.anvil._sector_manager.Sector
)  # value = Sector(start=0, stop=8192)
LZ4_HEADER: _struct.Struct  # value = <_struct.Struct object>
LZ4_MAGIC: bytes  # value = b'LZ4Block'
MaxRegionSize: int = 1044480
SectorSize: int = 4096
log: logging.Logger  # value = <Logger amulet.level.java.anvil._region (INFO)>
