from __future__ import annotations

import os
import struct
from typing import (
    Tuple,
    Dict,
    Generator,
    Set,
    Union,
    Optional,
    List,
    TYPE_CHECKING,
    BinaryIO,
)
from io import BytesIO

import amulet_nbt as nbt

from amulet.utils.format_utils import check_all_exist
from amulet.api.errors import ChunkDoesNotExist, LevelDoesNotExist
from amulet.api.data_types import ChunkCoordinates
from amulet.api.wrapper.world_format_wrapper import WorldFormatWrapper
from amulet.world_interface.chunk import interfaces
from amulet.libs.leveldb import LevelDB

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_chunk_versions import (
    game_to_chunk_version,
)

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface
    from amulet.api.data_types import Dimension

InternalDimension = Optional[int]


class LevelDBLevelManager:
    # tag_ids = {45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 118}

    def __init__(self, directory: str):
        self._directory = directory
        self._db = LevelDB(os.path.join(self._directory, "db"))
        # self._levels format Dict[level, Dict[Tuple[cx, cz], List[Tuple[full_key, key_extension]]]]
        self._levels: Dict[InternalDimension, Set[ChunkCoordinates]] = {}
        self._dimension_name_map: Dict["Dimension", InternalDimension] = {}
        self._batch_temp: Dict[bytes, Union[bytes, None]] = {}

        self.register_dimension(None, "overworld")
        self.register_dimension(1, "nether")
        self.register_dimension(2, "end")

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
            raise LevelDoesNotExist(dimension)

    def all_chunk_coords(self, dimension: "Dimension") -> Set[ChunkCoordinates]:
        internal_dimension = self._get_internal_dimension(dimension)
        if internal_dimension in self._levels:
            return self._levels[internal_dimension]
        else:
            return set()

    def _add_chunk(self, key_: bytes, has_level: bool = False):
        if has_level:
            cx, cz, level = struct.unpack("<iii", key_[:12])
        else:
            cx, cz = struct.unpack("<ii", key_[:8])
            level = None
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
                if internal_dimension is None:
                    if 9 <= len(key) <= 10:
                        key_extension = key[8:]
                    else:
                        continue
                else:
                    if (
                        13 <= len(key) <= 14
                        and struct.unpack("<i", key[8:12])[0] == internal_dimension
                    ):
                        key_extension = key[12:]
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
        if internal_dimension is None:
            key_prefix = struct.pack("<ii", cx, cz)
        else:
            key_prefix = struct.pack("<iii", cx, cz, internal_dimension)
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
                    if internal_dimension is None:
                        key_prefix = struct.pack("<ii", cx, cz)
                    else:
                        key_prefix = struct.pack("<iii", cx, cz, internal_dimension)

                    self._batch_temp[key_prefix + key] = None


class LevelDAT(nbt.NBTFile):
    def __init__(self, path: str):
        with open(path, "rb") as f:
            self._level_dat_version = struct.unpack("<i", f.read(4))[
                0
            ]  # TODO: handle other versions
            assert (
                4 <= self._level_dat_version <= 8
            ), f"Unknown level.dat version {self._level_dat_version}"
            data_length = struct.unpack("<i", f.read(4))[0]
            root_tag = nbt.load(
                buffer=f.read(data_length), compressed=False, little_endian=True
            )
        super().__init__(root_tag.value, root_tag.name)

    def save_to(
        self, filename_or_buffer: Union[str, BinaryIO] = None
    ) -> Optional[bytes]:
        buffer = BytesIO()
        buffer.write(struct.pack("<i", self._level_dat_version))
        buffer.write(super().save_to(compressed=False, little_endian=True))
        if filename_or_buffer is None:
            return buffer.getvalue()
        elif isinstance(filename_or_buffer, str):
            with open(filename_or_buffer, "wb") as f:
                f.write(buffer.getvalue())
        else:
            filename_or_buffer.write(buffer.getvalue())


class LevelDBFormat(WorldFormatWrapper):
    def __init__(self, directory: str):
        super().__init__(directory)
        self._lock = False
        self.root_tag: nbt.NBTFile = nbt.NBTFile()
        self._load_level_dat()
        self._level_manager: Optional[LevelDBLevelManager] = None

    def _load_level_dat(self):
        """Load the level.dat file and check the image file"""
        self.root_tag = LevelDAT(os.path.join(self.path, "level.dat"))
        if os.path.isfile(os.path.join(self.path, "world_icon.jpeg")):
            self._world_image_path = os.path.join(self.path, "world_icon.jpeg")

    @staticmethod
    def is_valid(directory):
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        if not check_all_exist(directory, "db", "level.dat", "levelname.txt"):
            return False

        return True

    @property
    def platform(self) -> str:
        """Platform string"""
        return "bedrock"

    def _get_version(self) -> Tuple[int, ...]:
        """The version the world was last opened in
        This should be greater than or equal to the chunk versions found within
        For this format wrapper it returns a tuple of 3/4 ints (the game version number)"""
        try:
            return tuple([t.value for t in self.root_tag["lastOpenedWithVersion"]])
        except Exception:
            return 1, 2, 0

    @property
    def world_name(self):
        """The name of the world"""
        return self.root_tag["LevelName"].value

    @world_name.setter
    def world_name(self, value: str):
        self.root_tag["LevelName"] = nbt.TAG_String(value)

    @property
    def last_played(self) -> int:
        return self.root_tag["LastPlayed"].value

    @property
    def game_version_string(self) -> str:
        try:
            return f'Bedrock {".".join(str(v.value) for v in self.root_tag["lastOpenedWithVersion"].value)}'
        except Exception:
            return f"Bedrock Unknown Version"

    @property
    def dimensions(self) -> List["Dimension"]:
        """A list of all the levels contained in the world"""
        self._verify_has_lock()
        return self._level_manager.dimensions

    def register_dimension(
        self, dimension_internal: int, dimension_name: Optional["Dimension"] = None
    ):
        """
        Register a new dimension.
        :param dimension_internal: The internal representation of the dimension
        :param dimension_name: The name of the dimension shown to the user
        :return:
        """
        self._level_manager.register_dimension(dimension_internal, dimension_name)

    def _get_interface(self, max_world_version, raw_chunk_data=None) -> "Interface":
        if raw_chunk_data:
            key = self._get_interface_key(raw_chunk_data)
        else:
            key = "bedrock", game_to_chunk_version(max_world_version[1])
        return interfaces.loader.get(key)

    def _get_interface_key(self, raw_chunk_data: Dict[bytes, bytes]) -> Tuple[str, int]:
        if b"," in raw_chunk_data:
            v = raw_chunk_data[b","][0]
        else:
            v = raw_chunk_data.get(b"v", "\x00")[0]
        return (
            self.platform,
            v,
        )  # TODO: work out a valid default

    def _reload_world(self):
        try:
            self.close()
        except:
            pass
        self._level_manager = LevelDBLevelManager(self.path)
        self._lock = True

    def open(self):
        """Open the database for reading and writing"""
        self._reload_world()

    @property
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

    def unload(self):
        """Unload data stored in the Format class"""
        pass

    def all_chunk_coords(
        self, dimension: "Dimension"
    ) -> Generator[ChunkCoordinates, None, None]:
        self._verify_has_lock()
        yield from self._level_manager.all_chunk_coords(dimension)

    def delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        self._verify_has_lock()
        self._level_manager.delete_chunk(cx, cz, dimension)

    def _put_raw_chunk_data(
        self, cx: int, cz: int, data: Dict[bytes, bytes], dimension: "Dimension", *args
    ):
        """
        Actually stores the data from the interface to disk.
        """
        self._verify_has_lock()
        return self._level_manager.put_chunk_data(cx, cz, data, dimension)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: "Dimension", *args
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
