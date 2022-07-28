from __future__ import annotations

import os
import struct
import warnings
from typing import Tuple, Dict, Union, Optional, List, BinaryIO, Iterable, Any
from io import BytesIO
import shutil
import traceback
import time

from amulet_nbt import (
    AbstractBaseTag,
    load as load_nbt,
    NamedTag,
    CompoundTag,
    StringTag,
    ByteTag,
    IntTag,
    ListTag,
    LongTag,
    FloatTag,
    utf8_escape_decoder,
    utf8_escape_encoder,
)
from amulet.api.player import Player, LOCAL_PLAYER
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionBox, SelectionGroup

from amulet.libs.leveldb import LevelDB, LevelDBException, LevelDBEncrypted
from amulet.utils.format_utils import check_all_exist
from amulet.api.data_types import (
    ChunkCoordinates,
    VersionNumberTuple,
    PlatformType,
    Dimension,
    AnyNDArray,
)
from amulet.api.wrapper import WorldFormatWrapper
from amulet.api.errors import ObjectWriteError, ObjectReadError, PlayerDoesNotExist

from .interface.chunk.leveldb_chunk_versions import (
    game_to_chunk_version,
)
from .dimension import (
    LevelDBDimensionManager,
    ChunkData,
    OVERWORLD,
    THE_NETHER,
    THE_END,
)
from .interface.chunk import BaseLevelDBInterface, get_interface

InternalDimension = Optional[int]


class BedrockLevelDAT(NamedTag):
    _path: str
    _level_dat_version: int

    def __init__(
        self, tag=None, name: str = "", path: str = None, level_dat_version: int = None
    ):
        if isinstance(tag, str):
            warnings.warn(
                "You must use BedrockLevelDAT.from_file to load from a file.",
                FutureWarning,
            )
            super().__init__()
            self._path = path = tag
            self._level_dat_version = 8
            if os.path.isfile(path):
                self.load_from(path)
            return
        else:
            if not (isinstance(path, str) and isinstance(level_dat_version, int)):
                raise TypeError(
                    "path and level_dat_version must be specified when constructing a BedrockLevelDAT instance."
                )
            super().__init__(tag, name)
            self._path = path
            self._level_dat_version = level_dat_version

    @classmethod
    def from_file(cls, path: str):
        level_dat_version, name, tag = cls._read_from(path)
        return cls(tag, name, path, level_dat_version)

    @property
    def path(self) -> Optional[str]:
        return self._path

    @staticmethod
    def _read_from(path: str) -> Tuple[int, str, AbstractBaseTag]:
        with open(path, "rb") as f:
            level_dat_version = struct.unpack("<i", f.read(4))[0]
            if 4 <= level_dat_version <= 9:
                data_length = struct.unpack("<i", f.read(4))[0]
                root_tag = load_nbt(
                    f.read(data_length),
                    compressed=False,
                    little_endian=True,
                    string_decoder=utf8_escape_decoder,
                )
                name = root_tag.name
                value = root_tag.tag
            else:
                # TODO: handle other versions
                raise ObjectReadError(
                    f"Unsupported level.dat version {level_dat_version}"
                )
        return level_dat_version, name, value

    def load_from(self, path: str):
        self._level_dat_version, self.name, self.tag = self._read_from(path)

    def reload(self):
        self.load_from(self.path)

    def save(self, path: str = None):
        self.save_to(path or self._path)

    def save_to(
        self,
        filename_or_buffer: Union[str, BinaryIO] = None,
        *,
        compressed=False,
        little_endian=True,
        string_encoder=utf8_escape_encoder,
    ) -> Optional[bytes]:
        payload = super().save_to(
            compressed=compressed,
            little_endian=little_endian,
            string_encoder=string_encoder,
        )
        buffer = BytesIO()
        buffer.write(struct.pack("<ii", self._level_dat_version, len(payload)))
        buffer.write(payload)
        if filename_or_buffer is None:
            return buffer.getvalue()
        elif isinstance(filename_or_buffer, str):
            with open(filename_or_buffer, "wb") as f:
                f.write(buffer.getvalue())
        else:
            filename_or_buffer.write(buffer.getvalue())


class LevelDBFormat(WorldFormatWrapper[VersionNumberTuple]):
    """
    This FormatWrapper class exists to interface with the Bedrock world format.
    """

    # The leveldb database. Access it through the public property `level_db`
    _db: Optional[LevelDB]
    # A class to manage dimension data. This is private
    _dimension_manager: Optional[LevelDBDimensionManager]

    _root_tag: BedrockLevelDAT

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`LevelDBFormat`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
        self._platform = "bedrock"
        dat_path = os.path.join(path, "level.dat")
        if os.path.isfile(dat_path):
            self._root_tag = BedrockLevelDAT.from_file(dat_path)
        else:
            # TODO: handle level creation better
            self._root_tag = BedrockLevelDAT(path=dat_path, level_dat_version=9)
        self._db = None
        self._dimension_manager = None
        self._shallow_load()

    def _shallow_load(self):
        try:
            self._load_level_dat()
        except:
            pass

    def _load_level_dat(self):
        """Load the level.dat file and check the image file"""
        if os.path.isfile(os.path.join(self.path, "world_icon.jpeg")):
            self._world_image_path = os.path.join(self.path, "world_icon.jpeg")
        self.root_tag = BedrockLevelDAT.from_file(os.path.join(self.path, "level.dat"))

    @staticmethod
    def is_valid(path: str):
        return check_all_exist(path, "db", "level.dat", "levelname.txt")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"bedrock": (True, True)}

    @property
    def version(self) -> VersionNumberTuple:
        if self._version is None:
            self._version = self._get_version()
        return self._version

    def _get_version(self) -> VersionNumberTuple:
        """
        The version the world was last opened in.

        This should be greater than or equal to the chunk versions found within

        For this format wrapper it returns a tuple of 3/4 ints (the game version number)
        """
        try:
            return tuple(
                [
                    t.py_int
                    for t in self.root_tag.compound.get_list("lastOpenedWithVersion")
                ]
            )
        except Exception:
            return 1, 2, 0

    @property
    def root_tag(self) -> BedrockLevelDAT:
        """The level.dat data for the level."""
        return self._root_tag

    @root_tag.setter
    def root_tag(self, root_tag: Union[NamedTag, CompoundTag, BedrockLevelDAT]):
        if isinstance(root_tag, CompoundTag):
            self._root_tag.tag = root_tag
        elif isinstance(root_tag, NamedTag):
            self._root_tag.name = root_tag.name
            self._root_tag.tag = root_tag.compound
        else:
            raise ValueError(
                "root_tag must be a CompoundTag, NamedTag or BedrockLevelDAT"
            )

    @property
    def level_name(self) -> str:
        return self.root_tag.compound.get_string("LevelName", StringTag()).py_str

    @level_name.setter
    def level_name(self, value: str):
        self.root_tag.compound["LevelName"] = StringTag(value)

    @property
    def last_played(self) -> int:
        return self.root_tag.compound.get_long("LastPlayed", LongTag()).py_int

    @property
    def game_version_string(self) -> str:
        try:
            return f'Bedrock {".".join(str(v.py_int) for v in self.root_tag.compound.get_list("lastOpenedWithVersion"))}'
        except Exception:
            return f"Bedrock Unknown Version"

    @property
    def dimensions(self) -> List["Dimension"]:
        self._verify_has_lock()
        return self._dimension_manager.dimensions

    # def register_dimension(
    #     self, dimension_internal: int, dimension_name: Optional["Dimension"] = None
    # ):
    #     """
    #     Register a new dimension.
    #
    #     :param dimension_internal: The internal integer representation of the dimension.
    #     :param dimension_name: The name of the dimension shown to the user.
    #     :return:
    #     """
    #     self._dimension_manager.register_dimension(dimension_internal, dimension_name)

    @property
    def level_db(self) -> LevelDB:
        """The raw leveldb database."""
        if self._db is None:
            raise Exception(
                "The world is not open. The leveldb database cannot be accessed."
            )
        return self._db

    @property
    def _level_manager(self) -> LevelDBDimensionManager:
        warnings.warn(
            "_level_manager attribute is depreciated. If you want to access the raw leveldb database it can be accessed through the level_db property."
        )
        return self._dimension_manager

    def _get_interface(
        self, raw_chunk_data: Optional[Any] = None
    ) -> BaseLevelDBInterface:
        return get_interface(self._get_interface_key(raw_chunk_data))

    def _get_interface_key(self, raw_chunk_data: Optional[ChunkData] = None) -> int:
        if raw_chunk_data:
            if b"," in raw_chunk_data:
                chunk_version = raw_chunk_data[b","][0]
            else:
                chunk_version = raw_chunk_data.get(b"v", b"\x00")[0]
        else:
            chunk_version = game_to_chunk_version(
                self.max_world_version[1],
                self.root_tag.compound.get_compound("experiments", CompoundTag())
                .get_byte("caves_and_cliffs", ByteTag())
                .py_int,
            )
        return chunk_version

    def _decode(
        self,
        interface: BaseLevelDBInterface,
        dimension: Dimension,
        cx: int,
        cz: int,
        raw_chunk_data: Any,
    ) -> Tuple[Chunk, AnyNDArray]:
        bounds = self.bounds(dimension).bounds
        return interface.decode(cx, cz, raw_chunk_data, (bounds[0][1], bounds[1][1]))

    def _encode(
        self,
        interface: BaseLevelDBInterface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
    ) -> Any:
        bounds = self.bounds(dimension).bounds
        return interface.encode(
            chunk,
            chunk_palette,
            self.max_world_version,
            (bounds[0][1], bounds[1][1]),
        )

    def _reload_world(self):
        try:
            self.close()
        except:
            pass
        try:
            self._db = LevelDB(os.path.join(self.path, "db"))
            self._dimension_manager = LevelDBDimensionManager(self)
            self._is_open = True
            self._has_lock = True
            experiments = self.root_tag.compound.get_compound(
                "experiments", CompoundTag()
            )
            if (
                experiments.get_byte("caves_and_cliffs", ByteTag()).py_int
                or experiments.get_byte("caves_and_cliffs_internal", ByteTag()).py_int
                or self.version >= (1, 18)
            ):
                self._bounds[OVERWORLD] = SelectionGroup(
                    SelectionBox(
                        (-30_000_000, -64, -30_000_000), (30_000_000, 320, 30_000_000)
                    )
                )
            else:
                self._bounds[OVERWORLD] = SelectionGroup(
                    SelectionBox(
                        (-30_000_000, 0, -30_000_000), (30_000_000, 256, 30_000_000)
                    )
                )
            self._bounds[THE_NETHER] = SelectionGroup(
                SelectionBox(
                    (-30_000_000, 0, -30_000_000), (30_000_000, 128, 30_000_000)
                )
            )
            self._bounds[THE_END] = SelectionGroup(
                SelectionBox(
                    (-30_000_000, 0, -30_000_000), (30_000_000, 256, 30_000_000)
                )
            )
        except LevelDBEncrypted as e:
            self._is_open = self._has_lock = False
            raise LevelDBException(
                "It looks like this world is from the marketplace.\nThese worlds are encrypted and cannot be edited."
            ) from e
        except LevelDBException as e:
            msg = str(e)
            self._is_open = self._has_lock = False
            # I don't know if there is a better way of handling this.
            if msg.startswith("IO error:") and msg.endswith(": Permission denied"):
                traceback.print_exc()
                raise LevelDBException(
                    f"Failed to load the database. The world may be open somewhere else.\n{msg}"
                ) from e
            else:
                raise e

    def _open(self):
        """Open the database for reading and writing"""
        self._reload_world()

    def _create(
        self,
        overwrite: bool,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        **kwargs,
    ):
        if os.path.isdir(self.path):
            if overwrite:
                shutil.rmtree(self.path)
            else:
                raise ObjectWriteError(
                    f"A world already exists at the path {self.path}"
                )

        version = self.translation_manager.get_version(
            self.platform, self.version
        ).version_number
        self._version = version + (0,) * (5 - len(version))

        self.root_tag = root = CompoundTag()
        root["StorageVersion"] = IntTag(8)
        root["lastOpenedWithVersion"] = ListTag([IntTag(i) for i in self._version])
        root["Generator"] = IntTag(1)
        root["LastPlayed"] = LongTag(int(time.time()))
        root["LevelName"] = StringTag("World Created By Amulet")

        os.makedirs(self.path, exist_ok=True)
        self.root_tag.save()

        db = LevelDB(os.path.join(self.path, "db"), True)
        db.close()

        self._reload_world()

    @property
    def has_lock(self) -> bool:
        if self._has_lock:
            return True  # TODO: implement a check to ensure access to the database
        return False

    def _save(self):
        os.makedirs(self.path, exist_ok=True)
        self.root_tag.save()
        with open(os.path.join(self.path, "levelname.txt"), "w") as f:
            f.write(self.level_name)

    def _close(self):
        self._db.close()
        self._db = None
        self._dimension_manager = None
        self._actor_counter = None

    def unload(self):
        pass

    def all_chunk_coords(self, dimension: "Dimension") -> Iterable[ChunkCoordinates]:
        self._verify_has_lock()
        yield from self._dimension_manager.all_chunk_coords(dimension)

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return self._dimension_manager.has_chunk(cx, cz, dimension)

    def _delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        self._dimension_manager.delete_chunk(cx, cz, dimension)

    def _put_raw_chunk_data(
        self, cx: int, cz: int, data: ChunkData, dimension: "Dimension"
    ):
        return self._dimension_manager.put_chunk_data(cx, cz, data, dimension)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: "Dimension"
    ) -> ChunkData:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        return self._dimension_manager.get_chunk_data(cx, cz, dimension)

    def all_player_ids(self) -> Iterable[str]:
        """
        Returns a generator of all player ids that are present in the level
        """
        yield from (
            pid[7:].decode("utf-8")
            for pid, _ in self._db.iterate(b"player_", b"player_\xFF")
        )
        if self.has_player(LOCAL_PLAYER):
            yield LOCAL_PLAYER

    def has_player(self, player_id: str) -> bool:
        if player_id != LOCAL_PLAYER:
            player_id = f"player_{player_id}"
        return player_id.encode("utf-8") in self._db

    def _load_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        player_nbt = self._get_raw_player_data(player_id).compound
        dimension = player_nbt["DimensionId"]
        if isinstance(dimension, IntTag) and IntTag(0) <= dimension <= IntTag(2):
            dimension_str = {
                0: OVERWORLD,
                1: THE_NETHER,
                2: THE_END,
            }[dimension.py_int]
        else:
            dimension_str = OVERWORLD

        # get the players position
        pos_data = player_nbt.get("Pos")
        if (
            isinstance(pos_data, ListTag)
            and len(pos_data) == 3
            and pos_data.list_data_type == FloatTag.tag_id
        ):
            position = tuple(map(float, pos_data))
            position = tuple(
                p if -100_000_000 <= p <= 100_000_000 else 0.0 for p in position
            )
        else:
            position = (0.0, 0.0, 0.0)

        # get the players rotation
        rot_data = player_nbt.get("Rotation")
        if (
            isinstance(rot_data, ListTag)
            and len(rot_data) == 2
            and rot_data.list_data_type == FloatTag.tag_id
        ):
            rotation = tuple(map(float, rot_data))
            rotation = tuple(
                p if -100_000_000 <= p <= 100_000_000 else 0.0 for p in rotation
            )
        else:
            rotation = (0.0, 0.0)

        return Player(
            player_id,
            dimension_str,
            position,
            rotation,
        )

    def _get_raw_player_data(self, player_id: str) -> NamedTag:
        if player_id == LOCAL_PLAYER:
            key = player_id.encode("utf-8")
        else:
            key = f"player_{player_id}".encode("utf-8")
        try:
            data = self._db.get(key)
        except KeyError:
            raise PlayerDoesNotExist(f"Player {player_id} doesn't exist")
        return load_nbt(
            data,
            compressed=False,
            little_endian=True,
            string_decoder=utf8_escape_decoder,
        )
