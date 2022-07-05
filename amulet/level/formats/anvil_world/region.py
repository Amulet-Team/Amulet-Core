from __future__ import annotations

import os
import struct
import zlib
import gzip
from typing import Tuple, Dict, Union, Generator, Optional, BinaryIO
import numpy
import time
import re
import threading

from amulet_nbt import NamedTag, load as load_nbt

from amulet.utils import world_utils
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.api.data_types import (
    ChunkCoordinates,
)

InternalDimension = str


class AnvilRegion:
    region_regex = re.compile(r"r\.(?P<rx>-?\d+)\.(?P<rz>-?\d+)\.mca")

    @staticmethod
    def get_coords(file_path: str) -> Tuple[Union[int, None], Union[int, None]]:
        file_path = os.path.basename(file_path)
        match = AnvilRegion.region_regex.fullmatch(file_path)
        if match is None:
            return None, None
        return int(match.group("rx")), int(match.group("rz"))

    def __init__(self, file_path: str, create=False, mcc=False):
        """
        A class wrapper for a region file
        :param file_path: The file path of the region file
        :param create: bool - if true will create the region from scratch. If false will try loading from disk
        """
        self._file_path = file_path
        self.rx, self.rz = self.get_coords(file_path)
        self._mcc = mcc  # create mcc file if the chunk is greater than 1MiB

        # [dirty, mod_time, data_length, data]  feel free to extend if you want to implement modifying in place and defragging
        # Value is Tuple[save time, compressed bytes]. # The latter can be None if the region file has been unloaded to track which chunks exist.
        # If a chunk does not exist on disk it simply won't exist in this dictionary
        self._chunks: Dict[ChunkCoordinates, Tuple[int, Optional[bytes]]] = {}

        # committed chunks stores chunks that have been committed but not saved to disk. Value is Tuple[save time, compressed bytes].
        # The latter can be None in which case the chunk has been deleted
        self._committed_chunks: Dict[ChunkCoordinates, Tuple[int, Optional[bytes]]] = {}

        self._lock = threading.Lock()
        if create:
            # create the region from scratch.
            self._loaded = True
        else:
            # mark the region to be loaded when needed
            self._loaded = False
            # shallow load the data
            file_size = os.path.getsize(self._file_path)
            if file_size > 4096 * 2:
                with open(self._file_path, "rb") as fp:
                    offsets = numpy.fromfile(fp, dtype=">u4", count=1024).reshape(
                        32, 32
                    )
                    for x in range(32):
                        for z in range(32):
                            offset = offsets[z, x]
                            if offset != 0:
                                self._chunks[(x, z)] = (0, None)

    def all_chunk_coords(self) -> Generator[ChunkCoordinates, None, None]:
        for (cx, cz), (_, chunk_) in self._committed_chunks.items():
            if chunk_ is not None:
                yield cx + self.rx * 32, cz + self.rz * 32
        for cx, cz in self._chunks.keys():
            if (cx, cz) not in self._committed_chunks:
                yield cx + self.rx * 32, cz + self.rz * 32

    def has_chunk(self, cx: int, cz: int) -> bool:
        if (cx, cz) in self._committed_chunks:
            return self._committed_chunks[(cx, cz)][1] is not None
        else:
            return (cx, cz) in self._chunks

    def _load_with_lock(self):
        with self._lock:
            self._load()

    def _load(self):
        """Load the data if it is not loaded.
        Note this method on its own is not thread safe. Use _load_with_lock or implement locks yourself."""
        if not self._loaded:
            mode = "rb+" if os.path.isfile(self._file_path) else "wb"
            with open(self._file_path, mode) as fp:
                fp: BinaryIO
                # check that the file is a multiple of 4096 bytes and extend if not
                # TODO: perhaps rewrite this in a way that is more readable
                file_size = os.path.getsize(self._file_path)
                if file_size & 0xFFF:
                    file_size = (file_size | 0xFFF) + 1
                    fp.truncate(file_size)

                # if the length of the region file is 0 extend it to 8KiB TODO (perhaps have some error)
                if file_size < world_utils.SECTOR_BYTES * 2:
                    file_size = world_utils.SECTOR_BYTES * 2
                    fp.truncate(file_size)

                # read the file and populate the internal database
                # self._file_size = file_size

                fp.seek(0)

                # offsets = fp.read(world_utils.SECTOR_BYTES)
                # mod_times = fp.read(world_utils.SECTOR_BYTES)

                # self._free_sectors = free_sectors = numpy.full(
                #     file_size // world_utils.SECTOR_BYTES, True, bool
                # )
                # self._free_sectors[0:2] = False, False

                # the first array is made of 3 byte sector offset and 1 byte sector count
                sectors = (
                    numpy.fromfile(fp, dtype=">u4", count=1024).reshape(32, 32) >> 8
                )
                mod_times = numpy.fromfile(fp, dtype=">u4", count=1024).reshape(32, 32)

                # for offset in offsets:
                #     sector = offset >> 8
                #     count = offset & 0xFF
                #
                #     for i in range(sector, sector + count):
                #         if i >= len(free_sectors):
                #             return False
                #
                #         free_sectors[i] = False

                for cx in range(32):
                    for cz in range(32):
                        sector = sectors[cz, cx]
                        if sector:
                            fp.seek(world_utils.SECTOR_BYTES * sector)
                            # read int value and then read that amount of data
                            buffer_size_bytes: bytes = fp.read(4)
                            buffer_size = struct.unpack(">I", buffer_size_bytes)[0]
                            buffer: bytes = fp.read(buffer_size)

                            if buffer:
                                if buffer[0] & 128:  # if the "external" bit is set
                                    if self._mcc:
                                        mcc_path = os.path.join(
                                            os.path.dirname(self._file_path),
                                            f"c.{cx + self.rx * 32}.{cz + self.rz * 32}.mcc",
                                        )
                                        if os.path.isfile(mcc_path):
                                            with open(mcc_path, "rb") as f:
                                                buffer = (
                                                    bytes([buffer[0] & 127]) + f.read()
                                                )
                                        else:
                                            # the external flag was set but the external file cannot be found. Continue as if the chunk does not exist.
                                            continue
                                    else:
                                        # External bit set but this version cannot handle mcc files. Continue as if the chunk does not exist.
                                        continue

                                self._chunks[(cx, cz)] = (
                                    mod_times[cz, cx],
                                    buffer,
                                )

            self._loaded = True

    def unload(self):
        """Unload the data if it is not being used."""
        if not self._lock.locked():
            # if the data is not being used
            with self._lock:
                # acquire the lock and unload the data
                for key in self._chunks.keys():
                    self._chunks[key] = (0, None)
                self._loaded = False

    def save(self):
        if self._committed_chunks:
            with self._lock:
                # acquire the lock so that it cannot get unloaded while saving.
                self._load()
                if self._mcc:
                    mcc_chunks = {(cx, cz) for cx in range(32) for cz in range(32)}
                else:
                    mcc_chunks = set()
                for key, val in self._committed_chunks.items():
                    if val[1] is not None:
                        if self._mcc or len(val[1]) <= 2**20 - 4:
                            self._chunks[key] = val
                    elif key in self._chunks:
                        del self._chunks[key]
                self._committed_chunks.clear()
                offsets = numpy.zeros(1024, dtype=">u4")
                mod_times = numpy.zeros(1024, dtype=">u4")
                offset = 2
                data = []
                for (cx, cz), (mod_time, buffer) in self._chunks.items():
                    if buffer is not None:
                        index = cx + (cz << 5)
                        buffer_size = len(buffer)
                        if (
                            buffer_size > 2**20 - 4
                        ):  # if mcc is false the chunks that are too large should have already been removed.
                            mcc_chunks.remove((cx, cz))
                            with open(
                                os.path.join(
                                    os.path.dirname(self._file_path),
                                    f"c.{cx + self.rx * 32}.{cz + self.rz * 32}.mcc",
                                ),
                                "wb",
                            ) as f:
                                f.write(buffer[1:])
                            buffer = bytes([buffer[0] | 128])  # set the external flag
                            buffer_size = 1

                        sector_count = ((buffer_size + 4 | 0xFFF) + 1) >> 12
                        offsets[index] = (offset << 8) + sector_count
                        mod_times[index] = mod_time
                        data.append(
                            struct.pack(">I", buffer_size)
                            + buffer
                            + b"\x00" * ((sector_count << 12) - buffer_size - 4)
                        )
                        offset += sector_count
                os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
                with open(self._file_path, "wb") as fp:
                    fp.write(
                        struct.pack(">1024I", *offsets)
                    )  # there is probably a prettier way of doing this
                    fp.write(
                        struct.pack(">1024I", *mod_times)
                    )  # but I could not work it out with Numpy
                    fp.write(b"".join(data))

                # remove orphaned mcc files
                for cx, cz in mcc_chunks:
                    mcc_path = os.path.join(
                        os.path.dirname(self._file_path),
                        f"c.{cx + self.rx * 32}.{cz + self.rz * 32}.mcc",
                    )
                    if os.path.isfile(mcc_path):
                        os.remove(mcc_path)

    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """Get chunk data. Coords are in region space."""
        if (cx, cz) in self._committed_chunks:
            # if the chunk exists in the committed but unsaved chunks return that
            data = self._committed_chunks[(cx, cz)][1]
            if data is not None:
                compress_type, data = data[0], data[1:]
                return self._decompress(compress_type, data)
        elif (cx, cz) in self._chunks:
            # otherwise if the chunk exists in the main database return that
            with self._lock:
                self._load()
                data: bytes = self._chunks[(cx, cz)][1]
                compress_type, data = data[0], data[1:]
                if data:
                    return self._decompress(compress_type, data)

        raise ChunkDoesNotExist

    def put_chunk_data(self, cx: int, cz: int, data: NamedTag):
        """compress the data and put it in the class database"""
        bytes_data = self._compress(data)
        self._committed_chunks[(cx, cz)] = (int(time.time()), bytes_data)

    def delete_chunk_data(self, cx: int, cz: int):
        self._committed_chunks[(cx, cz)] = (0, None)

    @staticmethod
    def _compress(data: NamedTag) -> bytes:
        """Convert an NamedTag into a compressed bytes object"""
        data = data.save_to(compressed=False)
        return b"\x02" + zlib.compress(data)

    @staticmethod
    def _decompress(compress_type: int, data: bytes) -> NamedTag:
        """Convert a bytes object into an NamedTag"""
        if compress_type == world_utils.VERSION_GZIP:
            return load_nbt(gzip.decompress(data), compressed=False)
        elif compress_type == world_utils.VERSION_DEFLATE:
            return load_nbt(zlib.decompress(data), compressed=False)
        raise ChunkLoadError(f"Invalid compression type {compress_type}")
