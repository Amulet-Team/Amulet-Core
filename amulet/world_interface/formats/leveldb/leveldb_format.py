from __future__ import annotations

import os
import struct
from typing import Tuple, Dict, Generator, Set, Union

import amulet_nbt as nbt

from amulet.utils.format_utils import check_all_exist
from amulet.world_interface.formats import Format
from amulet.world_interface.chunk import interfaces
from amulet.libs.leveldb import LevelDB
from amulet.api.errors import ChunkDoesNotExist, LevelDoesNotExist


class LevelDBLevelManager:
    # tag_ids = {45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 118}

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

    def all_chunk_coords(self, level: int = 0) -> Set[Tuple[int, int]]:
        if level in self._levels:
            return self._levels[level]
        else:
            raise LevelDoesNotExist

    def _add_chunk(self, key_: bytes, has_level: bool = False):
        if has_level:
            cx_, cz_, level_ = struct.unpack('<iii', key_[:12])
        else:
            cx_, cz_ = struct.unpack('<ii', key_[:8])
            level_ = 0
        self._levels.setdefault(level_, set()).add((cx_, cz_))

    def get_chunk_data(self, cx: int, cz: int, level: int = 0) -> Dict[bytes, bytes]:
        """Get a dictionary of chunk key extension in bytes to the raw data in the key.
        chunk key extension are the character(s) after <cx><cz>[level] in the key
        Will raise ChunkDoesNotExist if the chunk does not exist
        """
        iter_start = struct.pack('<ii', cx, cz)
        iter_end = struct.pack('<ii', cx, cz+1)
        if level in self._levels and (cx, cz) in self._levels[level]:
            chunk_data = {}
            for key, val in self._db.iterate(iter_start, iter_end):
                if level == 0:
                    if 9 <= len(key) <= 10:
                        key_extension = key[8:]
                    else:
                        continue
                else:
                    if 13 <= len(key) <= 14 and struct.unpack('<i', key[8:12])[0] == level:
                        key_extension = key[12:]
                    else:
                        continue
                chunk_data[key_extension] = val
            return chunk_data
        else:
            raise ChunkDoesNotExist

    def put_chunk_data(self, cx: int, cz: int, data: Dict[bytes, bytes], level: int = 0):
        """pass data to the region file class"""
        # get the region key
        self._levels.setdefault(level, set()).add((cx, cz))
        if level == 0:
            key_prefix = struct.pack('<ii', cx, cz)
        else:
            key_prefix = struct.pack('<iii', cx, cz, level)
        for key, val in data.items():
            self._batch_temp[key_prefix+key] = val

    def delete_chunk(self, cx: int, cz: int, level: int = 0):
        if level in self._levels and (cx, cz) in self._levels[level]:
            self._levels[level].remove((cx, cz))
            chunk_data = self.get_chunk_data(cx, cz, level)
            for key in chunk_data.keys():
                self._batch_temp[key] = None


class LevelDBFormat(Format):
    def __init__(self, directory: str):
        super().__init__(directory)
        with open(os.path.join(self._directory, "level.dat"), "rb") as f:
            self.root_tag = nbt.load(buffer=f.read()[8:])
        self._level_manager = LevelDBLevelManager(self._directory)

    @staticmethod
    def is_valid(directory):
        print(directory)
        if not check_all_exist(directory, "db", "level.dat", "levelname.txt"):
            return False

        return True

    def _max_world_version(self) -> Tuple[str, Tuple[int, int, int]]:
        return (
            "leveldb",
            tuple([t.value for t in self.root_tag["lastOpenedWithVersion"]]),
        )

    def _get_interface(
        self, max_world_version, raw_chunk_data=None
    ) -> interfaces.Interface:
        if raw_chunk_data:
            key = self._get_interface_key(raw_chunk_data)
        else:
            key = max_world_version  # TODO: bedrock does Interface versioning based on chunk version rather than game version
        return interfaces.loader.get(key)

    def _get_interface_key(self, raw_chunk_data: Dict[bytes, bytes]) -> Tuple[str, int]:
        return "leveldb", raw_chunk_data.get(b'v', 0)  # TODO: work out a valid default

    def save(self):
        self._level_manager.save()

    def close(self):
        self._level_manager.close()

    def all_chunk_coords(self, dimension: int = 0) -> Generator[Tuple[int, int]]:
        for coords in self._level_manager.all_chunk_coords(dimension):
            yield coords

    def delete_chunk(self, cx: int, cz: int, dimension: int = 0):
        self._level_manager.delete_chunk(cx, cz, dimension)

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Dict[bytes, bytes], dimension: int = 0):
        """
        Actually stores the data from the interface to disk.
        """
        return self._level_manager.put_chunk_data(cx, cz, data, dimension)

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: int = 0) -> Dict[bytes, bytes]:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        return self._level_manager.get_chunk_data(cx, cz, dimension)


FORMAT_CLASS = LevelDBFormat
