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
from amulet.api.errors import ChunkDoesNotExist, LevelDoesNotExist, ChunkLoadError


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
        self._chunks: Dict[Tuple[int, int], Tuple[int, bytes]] = {}

        self._committed_chunks: Dict[Tuple[int, int], Tuple[int, bytes]] = {}

        if create:
            # create the region from scratch.
            self._loaded = True
        else:
            # mark the region to be loaded when needed
            self._loaded = False
            # shallow load the data
            with open(self._file_path, "rb") as fp:
                offsets = numpy.fromfile(fp, dtype=">u4", count=1024).reshape(32, 32)
                for x in range(32):
                    for z in range(32):
                        offset = offsets[x, z]
                        if offset != 0:
                            self._chunks[(x, z)] = (0, b"")

    def all_chunk_coords(self) -> Generator[Tuple[int, int]]:
        for cx, cz in self._chunks.keys():
            yield cx + self.rx * 32, cz + self.rz * 32
        for cx, cz in self._committed_chunks.keys():
            if (cx, cz) not in self._chunks:
                yield self._committed_chunks[cx, cz]

    def _load(self):
        if not self._loaded:
            with open(self._file_path, "rb") as fp:
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
                sectors = numpy.fromfile(fp, dtype=">u4", count=1024).reshape(32, 32) >> 8
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

                self._chunks = {}
                for x in range(32):
                    for z in range(32):
                        sector = sectors[x, z]
                        if sector:
                            fp.seek(world_utils.SECTOR_BYTES * sector)
                            # read int value and then read that amount of data
                            buffer_size = struct.unpack(">I", fp.read(4))[0]
                            self._chunks[(x, z)] = (
                                mod_times[x, z],
                                fp.read(buffer_size),
                            )

            self._loaded = True

    def unload(self):
        for key in self._chunks.keys():
            self._chunks[key] = (0, b"")
        self._loaded = False

    def save(self):
        if self._committed_chunks:
            self._load()
            for key, val in self._committed_chunks.items():
                self._chunks[key] = val
            self._committed_chunks.clear()
            offsets = numpy.zeros(1024, dtype=">u4")
            mod_times = numpy.zeros(1024, dtype=">u4")
            offset = 2
            data = []
            for (
                (cx, cz),
                (mod_time, buffer),
            ) in self._chunks.items():
                if buffer:
                    index = cx + (cz << 5)
                    buffer_size = len(buffer)
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
        if (cx, cz) in self._committed_chunks:
            # if the chunk exists in the committed but unsaved chunks return that
            data = self._committed_chunks[(cx, cz)][1]
            if data:
                return self._decompress(data)
        elif (cx, cz) in self._chunks:
            # otherwise if the chunk exists in the main database return that
            self._load()
            data = self._chunks[(cx, cz)][1]
            if data:
                return self._decompress(self._chunks[(cx, cz)][3])

        raise ChunkDoesNotExist

    def put_chunk_data(self, cx: int, cz: int, data: nbt.NBTFile):
        """compress the data and put it in the class database"""
        bytes_data = self._compress(data)
        self._committed_chunks[(cx, cz)] = (int(time.time()), bytes_data)

    def delete_chunk_data(self, cx: int, cz: int):
        self._committed_chunks[(cx, cz)] = (0, b'')

    @staticmethod
    def _compress(data: nbt.NBTFile) -> bytes:
        """Convert an NBTFile into a compressed bytes object"""
        data = data.save_to(compressed=False)
        return b"\x02" + zlib.compress(data)

    @staticmethod
    def _decompress(data: bytes) -> nbt.NBTFile:
        """Convert a bytes object into an NBTFile"""
        if data[0] == world_utils.VERSION_GZIP:
            return nbt.load(buffer=gzip.decompress(data[1:]), compressed=False)
        elif data[0] == world_utils.VERSION_DEFLATE:
            return nbt.load(buffer=zlib.decompress(data[1:]), compressed=False)
        raise ChunkLoadError(f"Invalid compression type {data[0]}")


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
            yield from region.all_chunk_coords()

    def save(self, unload=True):
        # use put_chunk_data to actually upload modified chunks
        # run this to push those changes to disk

        for region in self._regions.values():
            region.save()
            if unload:
                region.unload()

    def close(self):
        pass

    def unload(self):
        for region in self._regions.values():
            region.unload()

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
    _level_names = {-1: "nether", 0: "overworld", 1: "end"}

    def __init__(self, directory: str):
        super().__init__(directory)
        self.root_tag: nbt.NBTFile = nbt.NBTFile()
        self._load_level_dat()
        self._levels: Dict[int, AnvilLevelManager] = {}
        self._lock = None

    def _load_level_dat(self):
        """Load the level.dat file and check the image file"""
        self.root_tag = nbt.load(filename=os.path.join(self._world_path, "level.dat"))
        if os.path.isfile(os.path.join(self._world_path, "icon.png")):
            self._world_image_path = os.path.join(self._world_path, "icon.png")
        else:
            self._world_image_path = self._missing_world_icon

    @staticmethod
    def is_valid(directory) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        if not check_all_exist(directory, "region", "level.dat"):
            return False

        if not check_one_exists(directory, "playerdata", "players"):
            return False

        level_dat_root = load_leveldat(directory)

        if "FML" in level_dat_root:
            return False

        return True

    @property
    def platform(self) -> str:
        """Platform string"""
        return "java"

    def _max_world_version(self) -> Tuple[str, int]:
        """The version the world was last opened in
        This should be greater than or equal to the chunk versions found within
        For this format wrapper it returns a single int DataVersion"""
        return (
            self.platform,
            self.root_tag.get("Data", nbt.TAG_Compound())
            .get("DataVersion", nbt.TAG_Int(-1))
            .value,
        )

    @property
    def world_name(self) -> str:
        """The name of the world"""
        return self.root_tag["Data"]["LevelName"].value

    @world_name.setter
    def world_name(self, value: str):
        self.root_tag["Data"]["LevelName"] = nbt.TAG_String(value)

    @property
    def game_version_string(self) -> str:
        try:
            return f'Java {self.root_tag["Data"]["Version"]["Name"].value}'
        except Exception:
            return f"Java Unknown Version"

    @property
    def dimensions(self) -> Dict[str, int]:
        """A list of all the levels contained in the world"""
        dimensions = {val: key for key, val in self._level_names.items()}
        for level in self._levels.keys():
            if level not in self._level_names:
                dimensions[f"DIM{level}"] = level

        return dimensions

    def _get_interface_key(self, raw_chunk_data) -> Tuple[str, int]:
        return self.platform, raw_chunk_data.get("DataVersion", nbt.TAG_Int(-1)).value

    def _reload_world(self):
        # reload the level.dat in case it has changed
        self._load_level_dat()

        # create the session.lock file (this has mostly been lifted from MCEdit)
        self._lock = int(time.time() * 1000)
        with open(os.path.join(self._world_path, "session.lock"), "wb") as f:
            f.write(struct.pack(">Q", self._lock))
            f.flush()
            os.fsync(f.fileno())

        # load all the levels
        self._levels: Dict[int, AnvilLevelManager] = {
            0: AnvilLevelManager(self._world_path)
        }
        for dir_name in os.listdir(self._world_path):
            level_path = os.path.join(self._world_path, dir_name)
            if os.path.isdir(level_path) and dir_name.startswith("DIM"):
                match = AnvilLevelManager.level_regex.fullmatch(dir_name)
                if match is None:
                    continue
                level = int(match.group("level"))
                self._levels[level] = AnvilLevelManager(level_path)

    def open(self):
        """Open the database for reading and writing"""
        self._reload_world()

    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        try:
            with open(os.path.join(self._world_path, "session.lock"), "rb") as f:
                return struct.unpack(">Q", f.read(8))[0] == self._lock
        except Exception:
            return False

    def save(self):
        """Save the data back to the disk database"""
        self._verify_has_lock()
        for level in self._levels.values():
            level.save()
        # TODO: save other world data
        self._changed = False

    def close(self):
        """Close the disk database"""
        pass

    def unload(self):
        """Unload data stored in the Format class"""
        for level in self._levels.values():
            level.unload()

    def _get_level(self, level: int):
        self._verify_has_lock()
        if level in self._levels:
            return self._levels[level]
        else:
            raise LevelDoesNotExist

    def all_chunk_coords(self, dimension: int = 0) -> Generator[Tuple[int, int]]:
        """A generator of all chunk coords in the given dimension"""
        for chunk_ in self._get_level(dimension).all_chunk_coords():
            yield chunk_

    def delete_chunk(self, cx: int, cz: int, dimension: int = 0):
        """Delete a chunk from a given dimension"""
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


FORMAT_CLASS = AnvilFormat

if __name__ == "__main__":
    import sys

    world_path = sys.argv[1]
    world = AnvilLevelManager(world_path)
    chunk = world.get_chunk_data(0, 0)
    print(chunk)
    world.put_chunk_data(0, 0, chunk)
    world.save()
