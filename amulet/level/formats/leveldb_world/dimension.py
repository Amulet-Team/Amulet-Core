from __future__ import annotations

import os
import struct
from typing import (
    Dict,
    Set,
    Union,
    Optional,
    List,
    TYPE_CHECKING,
)

from amulet.api.errors import ChunkDoesNotExist, DimensionDoesNotExist
from amulet.api.data_types import ChunkCoordinates
from amulet.libs.leveldb import LevelDB

if TYPE_CHECKING:
    from amulet.api.data_types import Dimension

InternalDimension = int
OVERWORLD = "minecraft:overworld"
THE_NETHER = "minecraft:the_nether"
THE_END = "minecraft:the_end"


class LevelDBDimensionManager:
    # tag_ids = {45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 118}

    def __init__(self, directory: str):
        self._directory = directory
        self._db = LevelDB(os.path.join(self._directory, "db"))
        # self._levels format Dict[level, Dict[Tuple[cx, cz], List[Tuple[full_key, key_extension]]]]
        self._levels: Dict[InternalDimension, Set[ChunkCoordinates]] = {}
        self._dimension_name_map: Dict["Dimension", InternalDimension] = {}
        self._batch_temp: Dict[bytes, Union[bytes, None]] = {}

        self.register_dimension(0, OVERWORLD)
        self.register_dimension(1, THE_NETHER)
        self.register_dimension(2, THE_END)

        for key in self._db.keys():
            if 9 <= len(key) <= 10 and key[8] in [44, 118]:  # "," "v"
                self._add_chunk(key)

            elif 13 <= len(key) <= 14 and key[12] in [44, 118]:  # "," "v"
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
            dimension_name: "Dimension" = f"DIM{dimension_internal}"

        if (
            dimension_internal not in self._levels
            and dimension_name not in self._dimension_name_map
        ):
            self._levels[dimension_internal] = set()
            self._dimension_name_map[dimension_name] = dimension_internal

    def _get_internal_dimension(self, dimension: "Dimension") -> InternalDimension:
        if dimension in self._dimension_name_map:
            return self._dimension_name_map[dimension]
        else:
            raise DimensionDoesNotExist(dimension)

    def all_chunk_coords(self, dimension: "Dimension") -> Set[ChunkCoordinates]:
        internal_dimension = self._get_internal_dimension(dimension)
        if internal_dimension in self._levels:
            return self._levels[internal_dimension]
        else:
            return set()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        internal_dimension = self._get_internal_dimension(dimension)
        return (
            internal_dimension in self._levels
            and (cx, cz) in self._levels[internal_dimension]
        )

    def _add_chunk(self, key_: bytes, has_level: bool = False):
        if has_level:
            cx, cz, level = struct.unpack("<iii", key_[:12])
        else:
            cx, cz = struct.unpack("<ii", key_[:8])
            level = 0
        if level not in self._levels:
            self.register_dimension(level)
        self._levels[level].add((cx, cz))

    def get_chunk_data(
        self, cx: int, cz: int, dimension: "Dimension"
    ) -> Dict[bytes, bytes]:
        """Get a dictionary of chunk key extension in bytes to the raw data in the key.
        chunk key extension are the character(s) after <cx><cz>[level] in the key
        Will raise ChunkDoesNotExist if the chunk does not exist
        """
        iter_start = struct.pack("<ii", cx, cz)
        iter_end = iter_start + b"\xff"
        internal_dimension = self._get_internal_dimension(dimension)
        if (
            internal_dimension in self._levels
            and (cx, cz) in self._levels[internal_dimension]
        ):
            chunk_data = {}
            for key, val in self._db.iterate(iter_start, iter_end):
                if internal_dimension:
                    if (
                        13 <= len(key) <= 14
                        and struct.unpack("<i", key[8:12])[0] == internal_dimension
                    ):
                        key_extension = key[12:]
                    else:
                        continue
                else:
                    if 9 <= len(key) <= 10:
                        key_extension = key[8:]
                    else:
                        continue

                chunk_data[key_extension] = val
            return chunk_data
        else:
            raise ChunkDoesNotExist

    def put_chunk_data(
        self, cx: int, cz: int, data: Dict[bytes, bytes], dimension: "Dimension"
    ):
        """pass data to the region file class"""
        # get the region key
        internal_dimension = self._get_internal_dimension(dimension)
        self._levels[internal_dimension].add((cx, cz))
        if internal_dimension:
            key_prefix = struct.pack("<iii", cx, cz, internal_dimension)
        else:
            key_prefix = struct.pack("<ii", cx, cz)

        for key, val in data.items():
            self._batch_temp[key_prefix + key] = val

    def delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        if dimension in self._dimension_name_map:
            internal_dimension = self._dimension_name_map[dimension]
            if (
                internal_dimension in self._levels
                and (cx, cz) in self._levels[internal_dimension]
            ):
                chunk_data = self.get_chunk_data(cx, cz, dimension)
                self._levels[internal_dimension].remove((cx, cz))
                for key in chunk_data.keys():
                    if internal_dimension:
                        key_prefix = struct.pack("<iii", cx, cz, internal_dimension)
                    else:
                        key_prefix = struct.pack("<ii", cx, cz)

                    self._batch_temp[key_prefix + key] = None
