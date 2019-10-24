from __future__ import annotations

import os
import struct
from typing import Tuple

import amulet_nbt as nbt

from amulet.utils.format_utils import check_all_exist
from amulet.world_interface.formats import Format
from amulet.world_interface import interfaces
from amulet.libs.leveldb import LevelDB


class LevelDBFormat(Format):
    def __init__(self, *args):
        super().__init__(*args)
        with open(os.path.join(self._directory, "level.dat"), "rb") as f:
            self.root_tag = nbt.load(buffer=f.read()[8:])
        self._db = LevelDB(os.path.join(self._directory, "db"))

    def save(self):
        raise NotImplementedError

    def close(self):
        self._db.close()

    def _max_world_version(self) -> Tuple:
        return 'leveldb', [t.value for t in self.root_tag.value["MinimumCompatibleClientVersion"]]

    def _get_raw_chunk_data(self, cx, cz) -> Tuple[int, int, LevelDB]:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        return (cx, cz, self._db)

    def _get_interface(self, max_world_version, raw_chunk_data=None) -> interfaces.Interface:
        if raw_chunk_data is not None:
            cx, cz = raw_chunk_data[:2]
            chunk_key_base = struct.pack("<ii", cx, cz)
            chunk_version = self._db.get(chunk_key_base + b"v")[0]
            key = ("leveldb", chunk_version)
        else:
            key = max_world_version
        return interfaces.get_interface(key)

    @staticmethod
    def is_valid(directory):
        print(directory)
        if not check_all_exist(directory, "db", "level.dat", "levelname.txt"):
            return False

        return True


FORMAT_CLASS = LevelDBFormat
