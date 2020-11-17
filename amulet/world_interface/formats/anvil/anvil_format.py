from __future__ import annotations

import os
import struct
import zlib
import gzip
from typing import Tuple, Any, Dict, Union, Generator, Optional, List, TYPE_CHECKING
import numpy
import time
import re

import amulet_nbt as nbt

from amulet.api.wrapper.world_format_wrapper import WorldFormatWrapper
from amulet.utils import world_utils
from amulet.utils.format_utils import check_all_exist, load_leveldat
from amulet.api.errors import ChunkDoesNotExist, LevelDoesNotExist, ChunkLoadError
from amulet.api.data_types import ChunkCoordinates, RegionCoordinates

if TYPE_CHECKING:
    from amulet.api.data_types import Dimension

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
        for (cx, cz), (_, _) in self._chunks.items():
            if (cx, cz) not in self._committed_chunks:
                yield cx + self.rx * 32, cz + self.rz * 32

    def _load(self):
        if not self._loaded:
            mode = "rb+" if os.path.isfile(self._file_path) else "wb"
            with open(self._file_path, mode) as fp:
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

                self._chunks.clear()
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
        for key in self._chunks.keys():
            self._chunks[key] = (0, None)
        self._loaded = False

    def save(self):
        if self._committed_chunks:
            self._load()
            if self._mcc:
                mcc_chunks = {(cx, cz) for cx in range(32) for cz in range(32)}
            else:
                mcc_chunks = set()
            for key, val in self._committed_chunks.items():
                if val[1] is not None:
                    if self._mcc or len(val[1]) <= 2 ** 20 - 4:
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
                        buffer_size > 2 ** 20 - 4
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

    def get_chunk_data(self, cx: int, cz: int) -> nbt.NBTFile:
        """Get chunk data. Coords are in region space."""
        if (cx, cz) in self._committed_chunks:
            # if the chunk exists in the committed but unsaved chunks return that
            data = self._committed_chunks[(cx, cz)][1]
            if data is not None:
                compress_type, data = data[0], data[1:]
                return self._decompress(compress_type, data)
        elif (cx, cz) in self._chunks:
            # otherwise if the chunk exists in the main database return that
            self._load()
            data: bytes = self._chunks[(cx, cz)][1]
            compress_type, data = data[0], data[1:]
            if data:
                return self._decompress(compress_type, data)

        raise ChunkDoesNotExist

    def put_chunk_data(self, cx: int, cz: int, data: nbt.NBTFile):
        """compress the data and put it in the class database"""
        bytes_data = self._compress(data)
        self._committed_chunks[(cx, cz)] = (int(time.time()), bytes_data)

    def delete_chunk_data(self, cx: int, cz: int):
        self._committed_chunks[(cx, cz)] = (0, None)

    @staticmethod
    def _compress(data: nbt.NBTFile) -> bytes:
        """Convert an NBTFile into a compressed bytes object"""
        data = data.save_to(compressed=False)
        return b"\x02" + zlib.compress(data)

    @staticmethod
    def _decompress(compress_type: int, data: bytes) -> nbt.NBTFile:
        """Convert a bytes object into an NBTFile"""
        if compress_type == world_utils.VERSION_GZIP:
            return nbt.load(buffer=gzip.decompress(data), compressed=False)
        elif compress_type == world_utils.VERSION_DEFLATE:
            return nbt.load(buffer=zlib.decompress(data), compressed=False)
        raise ChunkLoadError(f"Invalid compression type {compress_type}")


class AnvilLevelManager:
    level_regex = re.compile(r"DIM(?P<level>-?\d+)")

    def __init__(self, directory: str, mcc=False):
        self._directory = directory
        self._regions: Dict[RegionCoordinates, AnvilRegion] = {}
        self._mcc = mcc

        # shallow load all of the existing region classes
        region_dir = os.path.join(self._directory, "region")
        if os.path.isdir(region_dir):
            for region_file_name in os.listdir(region_dir):
                rx, rz = AnvilRegion.get_coords(region_file_name)
                if rx is None:
                    continue
                self._regions[(rx, rz)] = AnvilRegion(
                    os.path.join(self._directory, "region", region_file_name),
                    mcc=self._mcc,
                )

    def all_chunk_coords(self) -> Generator[ChunkCoordinates, None, None]:
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
            self._regions[key] = AnvilRegion(file_path, True, mcc=self._mcc)
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


class AnvilFormat(WorldFormatWrapper):
    def __init__(self, directory: str):
        super().__init__(directory)
        self.root_tag: nbt.NBTFile = nbt.NBTFile()
        self._load_level_dat()
        self._levels: Dict[InternalDimension, AnvilLevelManager] = {}
        self._dimension_name_map: Dict["Dimension", InternalDimension] = {}
        self._mcc_support: Optional[bool] = None
        self._lock = None

    def _load_level_dat(self):
        """Load the level.dat file and check the image file"""
        self.root_tag = nbt.load(os.path.join(self.path, "level.dat"))
        if os.path.isfile(os.path.join(self.path, "icon.png")):
            self._world_image_path = os.path.join(self.path, "icon.png")
        else:
            self._world_image_path = self._missing_world_icon

    @staticmethod
    def is_valid(directory) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        if not check_all_exist(directory, "level.dat"):
            return False

        try:
            level_dat_root = load_leveldat(directory)
        except:
            return False

        if "Data" not in level_dat_root:
            return False

        if "FML" in level_dat_root:
            return False

        return True

    @property
    def platform(self) -> str:
        """Platform string"""
        return "java"

    def _get_version(self) -> int:
        return (
            self.root_tag.get("Data", nbt.TAG_Compound())
            .get("DataVersion", nbt.TAG_Int(-1))
            .value
        )

    @property
    def world_name(self) -> str:
        """The name of the world"""
        return self.root_tag["Data"]["LevelName"].value

    @world_name.setter
    def world_name(self, value: str):
        self.root_tag["Data"]["LevelName"] = nbt.TAG_String(value)

    @property
    def last_played(self) -> int:
        return self.root_tag["Data"]["LastPlayed"].value

    @property
    def game_version_string(self) -> str:
        try:
            return f'Java {self.root_tag["Data"]["Version"]["Name"].value}'
        except Exception:
            return f"Java Unknown Version"

    @property
    def dimensions(self) -> List["Dimension"]:
        """A list of all the levels contained in the world"""
        return list(self._dimension_name_map.keys())

    def register_dimension(
        self,
        dimension_internal: InternalDimension,
        dimension_name: Optional["Dimension"] = None,
    ):
        """
        Register a new dimension.
        :param dimension_internal: The internal representation of the dimension
        :param dimension_name: The name of the dimension shown to the user
        :return:
        """
        if dimension_name is None:
            dimension_name: "Dimension" = dimension_internal

        if dimension_internal:
            path = os.path.join(self.path, dimension_internal)
        else:
            path = self.path

        if (
            dimension_internal not in self._levels
            and dimension_name not in self._dimension_name_map
        ):
            self._levels[dimension_internal] = AnvilLevelManager(
                path, mcc=self._mcc_support
            )
            self._dimension_name_map[dimension_name] = dimension_internal

    def _get_interface_key(self, raw_chunk_data) -> Tuple[str, int]:
        return self.platform, raw_chunk_data.get("DataVersion", nbt.TAG_Int(-1)).value

    def _reload_world(self):
        # reload the level.dat in case it has changed
        self._load_level_dat()

        # create the session.lock file (this has mostly been lifted from MCEdit)
        self._lock = int(time.time() * 1000)
        with open(os.path.join(self.path, "session.lock"), "wb") as f:
            f.write(struct.pack(">Q", self._lock))
            f.flush()
            os.fsync(f.fileno())

        self._mcc_support = (
            self.version > 2203
        )  # the real number might actually be lower

        # load all the levels
        self.register_dimension("", "overworld")
        self.register_dimension("DIM-1", "nether")
        self.register_dimension("DIM1", "end")

        for dir_name in os.listdir(self.path):
            level_path = os.path.join(self.path, dir_name)
            if os.path.isdir(level_path) and dir_name.startswith("DIM"):
                if AnvilLevelManager.level_regex.fullmatch(dir_name) is None:
                    continue
                self.register_dimension(dir_name)

    def open(self):
        """Open the database for reading and writing"""
        self._reload_world()

    @property
    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        try:
            with open(os.path.join(self.path, "session.lock"), "rb") as f:
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

    def _has_dimension(self, dimension: "Dimension"):
        return (
            dimension in self._dimension_name_map
            and self._dimension_name_map[dimension] in self._levels
        )

    def _get_dimension(self, dimension: "Dimension"):
        self._verify_has_lock()
        if self._has_dimension(dimension):
            return self._levels[self._dimension_name_map[dimension]]
        else:
            raise LevelDoesNotExist(dimension)

    def all_chunk_coords(
        self, dimension: "Dimension"
    ) -> Generator[ChunkCoordinates, None, None]:
        """A generator of all chunk coords in the given dimension"""
        if self._has_dimension(dimension):
            yield from self._get_dimension(dimension).all_chunk_coords()

    def delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        """Delete a chunk from a given dimension"""
        if self._has_dimension(dimension):
            self._get_dimension(dimension).delete_chunk(cx, cz)

    def _put_raw_chunk_data(
        self, cx: int, cz: int, data: Any, dimension: "Dimension", *args
    ):
        """
        Actually stores the data from the interface to disk.
        """
        self._get_dimension(dimension).put_chunk_data(cx, cz, data)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: "Dimension", *args
    ) -> nbt.NBTFile:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        return self._get_dimension(dimension).get_chunk_data(cx, cz)


FORMAT_CLASS = AnvilFormat

if __name__ == "__main__":
    import sys

    world_path = sys.argv[1]
    world = AnvilLevelManager(world_path)
    chunk = world.get_chunk_data(0, 0)
    print(chunk)
    world.put_chunk_data(0, 0, chunk)
    world.save()
