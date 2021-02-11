from __future__ import annotations

import os
import struct
from typing import (
    Tuple,
    Dict,
    Generator,
    Union,
    Optional,
    List,
    TYPE_CHECKING,
    BinaryIO,
)
from io import BytesIO

import amulet_nbt as nbt

from amulet.utils.format_utils import check_all_exist
from amulet.api.data_types import ChunkCoordinates, VersionNumberTuple, PlatformType
from amulet.api.wrapper import WorldFormatWrapper, DefaultVersion
from amulet.level import loader

from amulet.level.interfaces.chunk.leveldb.leveldb_chunk_versions import (
    game_to_chunk_version,
)
from .dimension import LevelDBDimensionManager

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface
    from amulet.api.data_types import Dimension

InternalDimension = Optional[int]


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
        self._platform = "bedrock"
        self.root_tag: nbt.NBTFile = nbt.NBTFile()
        self._load_level_dat()
        self._level_manager: Optional[LevelDBDimensionManager] = None
        self._shallow_load()

    def _shallow_load(self):
        raise NotImplementedError

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
        return check_all_exist(directory, "db", "level.dat", "levelname.txt")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"bedrock": (True, True)}

    @property
    def version(self) -> VersionNumberTuple:
        """The version number for the given platform the data is stored in eg (1, 16, 2)"""
        if self._version == DefaultVersion:
            self._version = self._get_version()
        return self._version

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

    def _get_interface_key(
        self, raw_chunk_data: Optional[Dict[bytes, bytes]] = None
    ) -> Tuple[str, int]:
        if raw_chunk_data:
            if b"," in raw_chunk_data:
                v = raw_chunk_data[b","][0]
            else:
                v = raw_chunk_data.get(b"v", b"\x00")[0]
        else:
            v = game_to_chunk_version(self.max_world_version[1])
        return (self.platform, v)  # TODO: work out a valid default

    def _reload_world(self):
        try:
            self.close()
        except:
            pass
        self._level_manager = LevelDBDimensionManager(self.path)
        self._lock = True

    def _open(self):
        """Open the database for reading and writing"""
        self._reload_world()

    def _create(self, path=None, platform=None, version=None, **kwargs):
        if path is None:
            raise ValueError("A path must be specified")
        if platform is None:
            raise ValueError("A platform must be specified")
        if version is None:
            raise ValueError("A version must be specified")

        level = LevelDBFormat(path)
        level.create_and_open(platform, version, **kwargs)
        level.save()
        level.close()

    @property
    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        if self._has_lock:
            return True  # TODO: implement a check to ensure access to the database
        return False

    def _save(self):
        self._level_manager.save()

    def _close(self):
        self._level_manager.close()

    def unload(self):
        """Unload data stored in the Format class"""
        pass

    def all_chunk_coords(
        self, dimension: "Dimension"
    ) -> Generator[ChunkCoordinates, None, None]:
        self._verify_has_lock()
        yield from self._level_manager.all_chunk_coords(dimension)

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return self._level_manager.has_chunk(cx, cz, dimension)

    def _delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        self._level_manager.delete_chunk(cx, cz, dimension)

    def _put_raw_chunk_data(
        self, cx: int, cz: int, data: Dict[bytes, bytes], dimension: "Dimension"
    ):
        """
        Actually stores the data from the interface to disk.
        """
        return self._level_manager.put_chunk_data(cx, cz, data, dimension)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: "Dimension"
    ) -> Dict[bytes, bytes]:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        return self._level_manager.get_chunk_data(cx, cz, dimension)
