from __future__ import annotations

import os
import struct
import zlib
import gzip
from typing import BinaryIO
from collections.abc import Iterator
import numpy
import time
import re
import threading
import logging
from enum import IntEnum

import lz4.block as lz4_block
from amulet_nbt import NamedTag, load as load_nbt

from amulet.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.api.data_types import (
    ChunkCoordinates,
)
from ._sector_manager import SectorManager, Sector

SectorSize = 0x1000
MaxRegionSize = 255 * SectorSize  # the maximum size data in the region file can be

log = logging.getLogger(__name__)


class RegionFileVersion(IntEnum):
    VERSION_GZIP = 1
    VERSION_DEFLATE = 2
    VERSION_NONE = 3
    VERSION_LZ4 = 4


LZ4_HEADER = struct.Struct("<8sBiii")
LZ4_MAGIC = b"LZ4Block"
COMPRESSION_METHOD_RAW = 0x10
COMPRESSION_METHOD_LZ4 = 0x20


def _decompress_lz4(data: bytes) -> bytes:
    """The LZ4 compression format is a sequence of LZ4 blocks with some header data."""
    # https://github.com/lz4/lz4-java/blob/7c931bef32d179ec3d3286ee71638b23ebde3459/src/java/net/jpountz/lz4/LZ4BlockInputStream.java#L200
    decompressed: list[bytes] = []
    index = 0
    while index < len(data):
        magic, token, compressed_length, original_length, checksum = LZ4_HEADER.unpack(
            data[index : index + LZ4_HEADER.size]
        )
        index += LZ4_HEADER.size
        compression_method = token & 0xF0
        if (
            magic != LZ4_MAGIC
            or original_length < 0
            or compressed_length < 0
            or (original_length == 0 and compressed_length != 0)
            or (original_length != 0 and compressed_length == 0)
            or (
                compression_method == COMPRESSION_METHOD_RAW
                and original_length != compressed_length
            )
        ):
            raise ValueError("LZ4 compressed block is corrupted.")
        if compression_method == COMPRESSION_METHOD_RAW:
            decompressed.append(data[index : index + original_length])
            index += original_length
        elif compression_method == COMPRESSION_METHOD_LZ4:
            decompressed.append(
                lz4_block.decompress(
                    data[index : index + compressed_length], original_length
                )
            )
            index += compressed_length
        else:
            raise ValueError("LZ4 compressed block is corrupted.")
    return b"".join(decompressed)


def _compress(tag: NamedTag) -> bytes:
    """Convert an NBTFile into a compressed bytes object"""
    data = tag.save_to(compressed=False)
    return b"\x02" + zlib.compress(data)


def _decompress(data: bytes) -> NamedTag:
    """Convert a bytes object into an NBTFile"""
    compress_type, data = data[0], data[1:]
    if compress_type == RegionFileVersion.VERSION_GZIP:
        return load_nbt(gzip.decompress(data), compressed=False)
    elif compress_type == RegionFileVersion.VERSION_DEFLATE:
        return load_nbt(zlib.decompress(data), compressed=False)
    elif compress_type == RegionFileVersion.VERSION_NONE:
        return load_nbt(data, compressed=False)
    elif compress_type == RegionFileVersion.VERSION_LZ4:
        return load_nbt(_decompress_lz4(data), compressed=False)
    raise ChunkLoadError(f"Invalid compression type {compress_type}")


def _sanitise_file(handler: BinaryIO) -> None:
    handler.seek(0, os.SEEK_END)
    file_size = handler.tell()
    if file_size & 0xFFF:
        # ensure the file is a multiple of 4096 bytes
        file_size = (file_size | 0xFFF) + 1
        handler.truncate(file_size)

    # if the length of the region file is less than 8KiB extend it to 8KiB
    if file_size < SectorSize * 2:
        file_size = SectorSize * 2
        handler.truncate(file_size)


class AnvilRegion:
    """
    A class to read and write Minecraft Java Edition Region files.
    Only one class should exist per region file at any given time otherwise bad things may happen.
    """

    region_regex = re.compile(r"r\.(?P<rx>-?\d+)\.(?P<rz>-?\d+)\.mca")

    __slots__ = (
        "_path",
        "_rx",
        "_rz",
        "_mcc",
        "_sector_manager",
        "_chunk_locations",
        "_lock",
    )

    # The path to the region file
    _path: str

    # The region coordinates
    _rx: int
    _rz: int

    # Is support for .mcc files enabled
    _mcc: bool

    # A class to track which sectors are reserved
    _sector_manager: SectorManager | None

    # A dictionary mapping the chunk coordinate to the location on disk
    _chunk_locations: dict[ChunkCoordinates, Sector]

    # A lock to limit access to multiple threads
    _lock: threading.RLock

    @classmethod
    def get_coords(cls, file_path: str) -> tuple[int, int]:
        """Parse a region file path to get the region coordinates."""
        file_path = os.path.basename(file_path)
        match = cls.region_regex.fullmatch(file_path)
        if match is None:
            raise ValueError(f"{file_path} is not a valid region file path.")
        return int(match.group("rx")), int(match.group("rz"))

    def __init__(self, file_path: str, *, mcc: bool = False) -> None:
        """
        A class wrapper for a region file
        :param file_path: The file path of the region file
        :param create: bool - if true will create the region from scratch. If false will try loading from disk
        """
        self._path = file_path
        self._rx, self._rz = self.get_coords(file_path)
        self._mcc = mcc  # create mcc file if the chunk is greater than 1MiB
        self._sector_manager = None
        self._chunk_locations = {}
        self._lock = threading.RLock()

    @property
    def path(self) -> str:
        """The file path to the region file."""
        return self._path

    @property
    def rx(self) -> int:
        """The region x coordinate."""
        return self._rx

    @property
    def rz(self) -> int:
        """The region z coordinate."""
        return self._rz

    def get_mcc_path(self, cx: int, cz: int) -> str:
        """Get the mcc path. Coordinates are world chunk coordinates."""
        return os.path.join(
            os.path.dirname(self._path),
            f"c.{cx}.{cz}.mcc",
        )

    def _load(self) -> None:
        with self._lock:
            if self._sector_manager is not None:
                return

            # Create the sector manager and ensure the header is not reservable
            self._sector_manager = SectorManager(0, 0x2000)
            self._sector_manager.reserve(Sector(0, 0x2000))

            if os.path.isfile(self._path):
                # Load the file and populate the sector manager
                with open(self._path, "rb+") as handler:
                    _sanitise_file(handler)
                    handler.seek(0)
                    location_table = numpy.fromfile(
                        handler, dtype=">u4", count=1024
                    ).reshape(32, 32)
                    for (cz, cx), sector_data in numpy.ndenumerate(location_table):
                        if sector_data:
                            sector_offset = (sector_data >> 8) * 0x1000
                            sector_size = (sector_data & 0xFF) * 0x1000
                            sector = Sector(sector_offset, sector_offset + sector_size)
                            self._sector_manager.reserve(sector)
                            self._chunk_locations[(cx + self.rx * 32, cz + self.rz * 32)] = sector

    def all_coords(self) -> Iterator[ChunkCoordinates]:
        """An iterable of chunk coordinates in world space."""
        self._load()
        yield from list(self._chunk_locations)

    def has_data(self, cx: int, cz: int) -> bool:
        """Does the chunk exists. Coords are in world space."""
        self._load()
        return (cx, cz) in self._chunk_locations

    def unload(self) -> None:
        """Unload the data if it is not being used."""
        with self._lock:
            self._sector_manager = None
            self._chunk_locations.clear()

    def get_data(self, cx: int, cz: int) -> NamedTag:
        self._load()
        sector = self._chunk_locations.get((cx, cz))
        if sector is None:
            raise ChunkDoesNotExist
        with self._lock:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            with open(self._path, "rb+") as handler:
                _sanitise_file(handler)
                handler.seek(0, os.SEEK_END)
                if handler.tell() < sector.stop:
                    # if the sector is beyond the end of the file
                    raise ChunkDoesNotExist

                handler.seek(sector.start)
                buffer_size_bytes: bytes = handler.read(4)
                buffer_size = struct.unpack(">I", buffer_size_bytes)[0]
                buffer: bytes = handler.read(buffer_size)

                if buffer:
                    if buffer[0] & 128:  # if the "external" bit is set
                        if self._mcc:
                            mcc_path = self.get_mcc_path(cx, cz)
                            if os.path.isfile(mcc_path):
                                with open(mcc_path, "rb") as f:
                                    return _decompress(
                                        bytes([buffer[0] & 127]) + f.read()
                                    )
                    else:
                        return _decompress(buffer)
        raise ChunkDoesNotExist

    def _write_data(self, cx: int, cz: int, data: bytes | None) -> None:
        assert self.rx * 32 <= cx < (self.rx + 1) * 32 and self.rz * 32 <= cz < (self.rz + 1) * 32
        if isinstance(data, bytes) and len(data) + 4 > MaxRegionSize and not self._mcc:
            # if the data is too large and mcc files are not supported then do nothing
            log.error(
                f"Could not save data {cx},{cz} in region file {self._path} because it was too large."
            )
            return

        with self._lock:
            self._load()
            sector_manager = self._sector_manager
            assert sector_manager is not None
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            handler: BinaryIO
            with open(
                self._path, "rb+" if os.path.isfile(self._path) else "wb+"
            ) as handler:
                _sanitise_file(handler)

                old_sector = self._chunk_locations.pop((cx, cz), None)
                if old_sector is not None:
                    # the chunk used to exist
                    handler.seek(old_sector.start + 4)
                    if self._mcc and handler.read(1)[0] & 127:
                        # if the file is stored externally delete the file
                        mcc_path = self.get_mcc_path(cx, cz)
                        if os.path.isfile(mcc_path):
                            os.remove(mcc_path)
                    sector_manager.free(old_sector)

                location = b"\x00\x00\x00\x00"

                if isinstance(data, bytes):
                    # find a memory location large enough to fit the data
                    if len(data) + 4 > MaxRegionSize:
                        # save externally (if mcc files are not supported the check at the top will filter large files out)
                        with open(self.get_mcc_path(cx, cz), "wb") as mcc:
                            mcc.write(data[1:])
                        data = bytes([data[0] | 128])
                    data = struct.pack(">I", len(data)) + data
                    sector_length = (len(data) | 0xFFF) + 1
                    sector = sector_manager.reserve_space(sector_length)
                    assert sector.start & 0xFFF == 0
                    self._chunk_locations[(cx, cz)] = sector
                    location = struct.pack(
                        ">I", (sector.start >> 4) + (sector_length >> 12)
                    )
                    handler.seek(sector.start)
                    handler.write(data)
                    _sanitise_file(handler)

                # write the header data
                handler.seek(4 * (cx - self.rx * 32 + (cz - self.rz * 32) * 32))
                handler.write(location)
                handler.seek(SectorSize - 4, os.SEEK_CUR)
                handler.write(struct.pack(">I", int(time.time())))

    def set_data(self, cx: int, cz: int, data: NamedTag) -> None:
        """Write the data to the region file."""
        bytes_data = _compress(data)
        self._write_data(cx, cz, bytes_data)

    def delete_data(self, cx: int, cz: int) -> None:
        """Delete the data from the region file."""
        self._write_data(cx, cz, None)
