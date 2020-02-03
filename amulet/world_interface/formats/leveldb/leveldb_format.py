from __future__ import annotations

import os
import struct
from typing import Tuple, Dict, Generator, Set, Union, List

import amulet_nbt as nbt

from amulet.utils.format_utils import check_all_exist
from amulet.world_interface.formats import Format
from amulet.world_interface.chunk import interfaces
from amulet.libs.leveldb import LevelDB
from amulet.api.errors import ChunkDoesNotExist, LevelDoesNotExist
from amulet.world_interface.chunk.interfaces.leveldb.leveldb_chunk_versions import (
    game_to_chunk_version,
)


class LevelDBLevelManager:
    # tag_ids = {45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 118}
    _level_names = {
        0: "overworld",
        1: "nether",
        2: "end"
    }

    def __init__(self, directory: str):
        self._directory = directory
        self._db = LevelDB(os.path.join(self._directory, "db"))
        # self._levels format Dict[level, Dict[Tuple[cx, cz], List[Tuple[full_key, key_extension]]]]
        self._levels: Dict[int, Set[Tuple[int, int]]] = {}
        self._batch_temp: Dict[bytes, Union[bytes, None]] = {}

        for key in self._db.keys():
            if 9 <= len(key) <= 10 and key[8] == 118:
                self._add_chunk(key)

            elif 13 <= len(key) <= 14 and key[12] == 118:
                self._add_chunk(key, has_level=True)

    def save(self):
        batch = {}
        for key, val in self._batch_temp.items():
            if val is None:
                self._db.delete(key)
            else:
                batch[key] = val
        self._db.putBatch(batch)
        self._batch_temp.clear()

    def close(self):
        self._db.close()

    @property
    def dimensions(self) -> List[Tuple[str, int]]:
        """A list of all the levels contained in the world"""
        dimensions = {}
        for level in self._levels.keys():
            if level in self._level_names:
                dimensions[self._level_names[level]] = level
            else:
                dimensions[f'DIM{level}'] = level

        return dimensions

    def all_chunk_coords(self, dimension: int = 0) -> Set[Tuple[int, int]]:
        if dimension in self._levels:
            return self._levels[dimension]
        else:
            raise LevelDoesNotExist

    def _add_chunk(self, key_: bytes, has_level: bool = False):
        if has_level:
            cx_, cz_, level_ = struct.unpack("<iii", key_[:12])
        else:
            cx_, cz_ = struct.unpack("<ii", key_[:8])
            level_ = 0
        self._levels.setdefault(level_, set()).add((cx_, cz_))

    def get_chunk_data(self, cx: int, cz: int, dimension: int = 0) -> Dict[bytes, bytes]:
        """Get a dictionary of chunk key extension in bytes to the raw data in the key.
        chunk key extension are the character(s) after <cx><cz>[level] in the key
        Will raise ChunkDoesNotExist if the chunk does not exist
        """
        iter_start = struct.pack("<ii", cx, cz)
        iter_end = iter_start + b'\xff'
        if dimension in self._levels and (cx, cz) in self._levels[dimension]:
            chunk_data = {}
            for key, val in self._db.iterate(iter_start, iter_end):
                if dimension == 0:
                    if 9 <= len(key) <= 10:
                        key_extension = key[8:]
                    else:
                        continue
                else:
                    if (
                        13 <= len(key) <= 14
                        and struct.unpack("<i", key[8:12])[0] == dimension
                    ):
                        key_extension = key[12:]
                    else:
                        continue
                chunk_data[key_extension] = val
            return chunk_data
        else:
            raise ChunkDoesNotExist

    def put_chunk_data(
        self, cx: int, cz: int, data: Dict[bytes, bytes], dimension: int = 0
    ):
        """pass data to the region file class"""
        # get the region key
        self._levels.setdefault(dimension, set()).add((cx, cz))
        if dimension == 0:
            key_prefix = struct.pack("<ii", cx, cz)
        else:
            key_prefix = struct.pack("<iii", cx, cz, dimension)
        for key, val in data.items():
            self._batch_temp[key_prefix + key] = val

    def delete_chunk(self, cx: int, cz: int, dimension: int = 0):
        if dimension in self._levels and (cx, cz) in self._levels[dimension]:
            chunk_data = self.get_chunk_data(cx, cz, dimension)
            self._levels[dimension].remove((cx, cz))
            for key in chunk_data.keys():
                if dimension:
                    key_prefix = struct.pack("<iii", cx, cz, dimension)
                else:
                    key_prefix = struct.pack("<ii", cx, cz)
                self._batch_temp[key_prefix + key] = None


class LevelDBFormat(Format):
    def __init__(self, directory: str):
        super().__init__(directory)
        self._lock = False
        self.root_tag: nbt.NBTFile = None
        self._load_level_dat()
        self._level_manager: LevelDBLevelManager = None

    def _load_level_dat(self):
        """Load the level.dat file and check the image file"""
        with open(os.path.join(self._world_path, "level.dat"), "rb") as f:
            level_dat_version = struct.unpack('<i', f.read(4))[0]  # TODO: handle other versions
            assert level_dat_version == 8, f'Unknown level.dat version {level_dat_version}'
            data_length = struct.unpack('<i', f.read(4))[0]
            self.root_tag = nbt.load(
                buffer=f.read(data_length), compressed=False, little_endian=True
            )
        if os.path.isfile(os.path.join(self._world_path, "world_icon.jpeg")):
            self._world_image_path = os.path.join(self._world_path, "world_icon.jpeg")

    @staticmethod
    def is_valid(directory):
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        print(directory)
        if not check_all_exist(directory, "db", "level.dat", "levelname.txt"):
            return False

        return True

    @property
    def platform(self) -> str:
        """Platform string"""
        return 'bedrock'

    def _max_world_version(self) -> Tuple[str, Tuple[int, int, int]]:
        """The version the world was last opened in
        This should be greater than or equal to the chunk versions found within
        For this format wrapper it returns a tuple of 3/4 ints (the game version number)"""
        return (
            self.platform,
            tuple([t.value for t in self.root_tag["lastOpenedWithVersion"]]),
        )

    @property
    def world_name(self):
        """The name of the world"""
        return self.root_tag["LevelName"].value

    @world_name.setter
    def world_name(self, value: str):
        self.root_tag["LevelName"] = nbt.TAG_String(value)

    @property
    def game_version_string(self) -> str:
        try:
            return f'Bedrock {".".join(str(v) for v in self.root_tag["lastOpenedWithVersion"].value)}'
        except:
            return f'Bedrock Unknown Version'

    @property
    def dimensions(self) -> Dict[str, int]:
        """A list of all the levels contained in the world"""
        self._verify_has_lock()
        return self._level_manager.dimensions

    def _get_interface(
            self, max_world_version, raw_chunk_data=None
    ) -> interfaces.Interface:
        if raw_chunk_data:
            key = self._get_interface_key(raw_chunk_data)
        else:
            key = "bedrock", game_to_chunk_version(max_world_version[1])
        return interfaces.loader.get(key)

    def _get_interface_key(self, raw_chunk_data: Dict[bytes, bytes]) -> Tuple[str, int]:
        return (
            self.platform,
            raw_chunk_data.get(b"v", "\x00")[0],
        )  # TODO: work out a valid default

    def _reload_world(self):
        # TODO: handle closing the level if it was already open before opening again
        self._level_manager = LevelDBLevelManager(self._world_path)
        self._lock = True

    def open(self):
        """Open the database for reading and writing"""
        self._reload_world()

    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        # TODO: work out how to do this properly
        return self._lock

    def save(self):
        self._verify_has_lock()
        self._level_manager.save()
        self._changed = False

    def close(self):
        self._verify_has_lock()
        self._level_manager.close()

    def all_chunk_coords(self, dimension: int = 0) -> Generator[Tuple[int, int]]:
        self._verify_has_lock()
        for coords in self._level_manager.all_chunk_coords(dimension):
            yield coords

    def delete_chunk(self, cx: int, cz: int, dimension: int = 0):
        self._verify_has_lock()
        self._level_manager.delete_chunk(cx, cz, dimension)

    def _put_raw_chunk_data(
        self, cx: int, cz: int, data: Dict[bytes, bytes], dimension: int = 0
    ):
        """
        Actually stores the data from the interface to disk.
        """
        self._verify_has_lock()
        return self._level_manager.put_chunk_data(cx, cz, data, dimension)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: int = 0
    ) -> Dict[bytes, bytes]:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        self._verify_has_lock()
        return self._level_manager.get_chunk_data(cx, cz, dimension)


FORMAT_CLASS = LevelDBFormat
