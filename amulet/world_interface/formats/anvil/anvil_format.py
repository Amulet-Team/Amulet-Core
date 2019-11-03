from __future__ import annotations

import os
import struct
import zlib
import gzip
from typing import Tuple, Any, Dict, Union, Generator
import numpy
import time
import re

import amulet_nbt as nbt

from amulet.world_interface.formats import Format
from amulet.utils import world_utils
from amulet.utils.format_utils import check_all_exist, check_one_exists, load_leveldat
from amulet.api.errors import ChunkDoesNotExist, LevelDoesNotExist


class AnvilRegion:
    region_regex = re.compile(r"r\.(?P<rx>-?\d+)\.(?P<rz>-?\d+)\.mca")

    @staticmethod
    def get_coords(file_path: str) -> Tuple[Union[int, None], Union[int, None]]:
        file_path = os.path.basename(file_path)
        match = AnvilRegion.region_regex.fullmatch(file_path)
        if match is None:
            return None, None
        return int(match.group("rx")), int(match.group("rz"))

    def __init__(self, file_path: str, create=False):
        """
        A class wrapper for a region file
        :param file_path: The file path of the region file
        :param create: bool - if true will create the region from scratch. If false will try loading from disk
        """
        self._file_path = file_path
        self.rx, self.rz = self.get_coords(file_path)

        # [dirty, mod_time, data_length, data]  feel free to extend if you want to implement modifying in place and defragging
        self._chunks: Dict[Tuple[int, int], Tuple[bool, int, int, bytes]] = {}
        self._dirty = False  # is a chunk in region dirty

        if create:
            # create the region from scratch.
            self._loaded = True
        else:
            # mark the region to be loaded when needed
            self._loaded = False
            # shallow load the data
            with open(self._file_path, "rb") as fp:
                offsets = numpy.fromfile(fp, dtype=">u4", count=1024)
                for x in range(32):
                    for z in range(32):
                        offset = offsets[x + 32 * z]
                        if offset != 0:
                            self._chunks[(x, z)] = None

    def all_chunk_coords(self) -> Generator[Tuple[int, int]]:
        for cx, cz in self._chunks.keys():
            yield cx + self.rx * 32, cz + self.rz * 32

    def _load(self):
        with open(self._file_path, "rb") as fp:
            # check that the file is a multiple of 4096 bytes and extend if not
            # TODO: perhaps rewrite this in a way that is more readable
            file_size = os.path.getsize(self._file_path)
            if file_size & 0xFFF:
                file_size = (file_size | 0xFFF) + 1
                fp.truncate(file_size)

            # if the length of the region file is 0 extend it to 8KiB TODO (perhaps have some error)
            if not file_size:
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

            offsets = numpy.fromfile(fp, dtype=">u4", count=1024)
            mod_times = numpy.fromfile(fp, dtype=">u4", count=1024)

            # for offset in offsets:
            #     sector = offset >> 8
            #     count = offset & 0xFF
            #
            #     for i in range(sector, sector + count):
            #         if i >= len(free_sectors):
            #             return False
            #
            #         free_sectors[i] = False

            for x in range(32):
                for z in range(32):
                    offset = offsets[x + 32 * z]
                    if offset == 0:
                        continue
                    sector = offset >> 8
                    # count = offset & 0xFF   # the number of sectors used
                    fp.seek(world_utils.SECTOR_BYTES * sector)
                    # read int value and then read that amount of data
                    buffer_size = struct.unpack(">I", fp.read(4))[0]
                    self._chunks[(x, z)] = (
                        False,
                        mod_times[x + 32 * z],
                        buffer_size,
                        fp.read(buffer_size),
                    )

        self._loaded = True

    def save(self):
        if self._dirty:
            if not self._loaded:
                self._load()
            offsets = numpy.zeros(1024, dtype=">u4")
            mod_times = numpy.zeros(1024, dtype=">u4")
            offset = 2
            data = []
            for (
                (cx, cz),
                (dirty, mod_time, buffer_size, buffer),
            ) in self._chunks.items():
                index = cx + (cz << 5)
                sector_count = ((buffer_size + 4 | 0xFFF) + 1) >> 12
                offsets[index] = (offset << 8) + sector_count
                mod_times[index] = mod_time
                data.append(
                    struct.pack(">I", buffer_size)
                    + buffer
                    + b"\x00" * ((sector_count << 12) - buffer_size - 4)
                )
                offset += sector_count
            with open(self._file_path, "wb") as fp:
                fp.write(
                    struct.pack(">1024I", *offsets)
                )  # there is probably a prettier way of doing this
                fp.write(
                    struct.pack(">1024I", *mod_times)
                )  # but I could not work it out with Numpy
                fp.write(b"".join(data))

    def get_chunk_data(self, cx: int, cz: int) -> nbt.NBTFile:
        if not self._loaded:
            self._load()
        if (cx, cz) in self._chunks:
            return self._decompress(self._chunks[(cx, cz)][3])
        else:
            raise ChunkDoesNotExist

    def put_chunk_data(self, cx: int, cz: int, data: nbt.NBTFile):
        """compress the data and put it in the class database"""
        if not self._loaded:
            self._load()
        self._dirty = True
        buffer_size, bytes_data = self._compress(data)
        self._chunks[(cx, cz)] = (True, int(time.time()), buffer_size, bytes_data)

    def delete_chunk_data(self, cx: int, cz: int):
        if not self._loaded:
            self._load()
        if (cx, cz) in self._chunks:
            del self._chunks[(cx, cz)]
            self._dirty = True

    @staticmethod
    def _compress(data: nbt.NBTFile) -> Tuple[int, bytes]:
        """Convert an NBTFile into a compressed bytes object"""
        data = data.save_to(compressed=False)
        data = b"\x02" + zlib.compress(data)
        return len(data), data

    @staticmethod
    def _decompress(data: bytes) -> nbt.NBTFile:
        """Convert a bytes object into an NBTFile"""
        if data[0] == world_utils.VERSION_GZIP:
            return nbt.load(buffer=gzip.decompress(data[1:]), compressed=False)
        elif data[0] == world_utils.VERSION_DEFLATE:
            return nbt.load(buffer=zlib.decompress(data[1:]), compressed=False)
        raise Exception(f"Invalid compression type {data[0]}")


class AnvilLevelManager:
    level_regex = re.compile(r"DIM(?P<level>-?\d+)")

    def __init__(self, directory: str):
        self._directory = directory
        self._regions: Dict[Tuple[int, int], AnvilRegion] = {}

        # shallow load all of the existing region classes
        region_dir = os.path.join(self._directory, "region")
        if os.path.isdir(region_dir):
            for region_file_name in os.listdir(region_dir):
                rx, rz = AnvilRegion.get_coords(region_file_name)
                if rx is None:
                    continue
                self._regions[(rx, rz)] = AnvilRegion(
                    os.path.join(self._directory, "region", region_file_name)
                )

    def all_chunk_coords(self) -> Generator[Tuple[int, int]]:
        for region in self._regions.values():
            for chunk in region.all_chunk_coords():
                yield chunk

    def save(self):
        # use put_chunk_data to actually upload modified chunks
        # run this to push those changes to disk

        for region in self._regions.values():
            region.save()
            # TODO: perhaps delete the region from loaded regions so that memory usage doesn't explode

    def close(self):
        raise NotImplementedError
        # any final closing requirements (I don't think there are any for anvil)

    def get_chunk_data(self, cx: int, cz: int) -> nbt.NBTFile:
        """Get an NBTFile of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
        # get the region key
        return self._get_region(cx, cz).get_chunk_data(cx & 0x1F, cz & 0x1F)

    def _get_region(self, cx: int, cz: int, create=False) -> AnvilRegion:
        key = rx, rz = world_utils.chunk_coords_to_region_coords(cx, cz)
        if key in self._regions:
            return self._regions[key]

        if create:
            file_path = os.path.join(self._directory, "region", f"r.{rx}.{rz}.mca")
            self._regions[key] = AnvilRegion(file_path, True)
        else:
            raise ChunkDoesNotExist

        return self._regions[key]

    def put_chunk_data(self, cx: int, cz: int, data: nbt.NBTFile):
        """pass data to the region file class"""
        # get the region key
        self._get_region(cx, cz, create=True).put_chunk_data(cx & 0x1F, cz & 0x1F, data)

    def delete_chunk(self, cx: int, cz: int):
        try:
            self._get_region(cx, cz).delete_chunk_data(cx & 0x1F, cz & 0x1F)
        except ChunkDoesNotExist:
            pass


class AnvilFormat(Format):
    def __init__(self, directory: str):
        super().__init__(directory)
        self.root_tag = nbt.load(filename=os.path.join(self._directory, "level.dat"))
        self._levels: Dict[int, AnvilLevelManager] = {
            0: AnvilLevelManager(self._directory)
        }
        for dir_name in os.listdir(self._directory):
            level_path = os.path.join(self._directory, dir_name)
            if os.path.isdir(level_path) and dir_name.startswith("DIM"):
                match = AnvilLevelManager.level_regex.fullmatch(dir_name)
                if match is None:
                    continue
                level = match.group("level")
                self._levels[level] = AnvilLevelManager(level_path)

    def _get_level(self, level: int):
        if level in self._levels:
            return self._levels[level]
        else:
            raise LevelDoesNotExist

    def all_chunk_coords(self, dimension: int = 0) -> Generator[Tuple[int, int]]:
        for chunk in self._get_level(dimension).all_chunk_coords():
            yield chunk

    def save(self):
        for level in self._levels.values():
            level.save()
        # TODO: save other world data

    def close(self):
        pass  # TODO: release lock file

    def _max_world_version(self) -> Tuple[str, int]:
        return "anvil", self.root_tag["Data"]["DataVersion"].value

    def delete_chunk(self, cx: int, cz: int, dimension: int = 0):
        self._get_level(dimension).delete_chunk(cx, cz)

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: int = 0):
        """
        Actually stores the data from the interface to disk.
        """
        self._get_level(dimension).put_chunk_data(cx, cz, data)

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: int = 0) -> Any:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        return self._get_level(dimension).get_chunk_data(cx, cz)

    def _get_interface_key(self, raw_chunk_data) -> Tuple[str, int]:
        return "anvil", raw_chunk_data["DataVersion"].value

    @staticmethod
    def is_valid(directory) -> bool:
        print(directory)
        if not check_all_exist(directory, "region", "level.dat"):
            return False

        if not check_one_exists(directory, "playerdata", "players"):
            return False

        level_dat_root = load_leveldat(directory)

        if "FML" in level_dat_root:
            return False

        return True


FORMAT_CLASS = AnvilFormat

if __name__ == "__main__":
    import sys

    world_path = sys.argv[1]
    world = AnvilLevelManager(world_path)
    chunk = world.get_chunk_data(0, 0)
    print(chunk)
    world.put_chunk_data(0, 0, chunk)
    world.save()
