from __future__ import annotations

import os
import struct
from typing import Tuple, Any, Dict, Generator, Optional, List, Union
import time
import glob
import shutil

import amulet_nbt as nbt
from amulet.api.player.player_manager import Player, LOCAL_PLAYER

from amulet.api.wrapper import WorldFormatWrapper, DefaultVersion
from amulet.utils.format_utils import check_all_exist, load_leveldat
from amulet.api.errors import DimensionDoesNotExist, ObjectWriteError, ChunkLoadError
from amulet.api.data_types import (
    ChunkCoordinates,
    VersionNumberInt,
    PlatformType,
    DimensionCoordinates,
)
from .dimension import AnvilDimensionManager
from amulet.api.data_types import Dimension
from amulet.api import level as api_level

InternalDimension = str


class AnvilFormat(WorldFormatWrapper):
    """
    This FormatWrapper class exists to interface with the Java world format.
    """

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`AnvilFormat`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
        self._platform = "java"
        self._root_tag: nbt.NBTFile = nbt.NBTFile()
        self._levels: Dict[InternalDimension, AnvilDimensionManager] = {}
        self._dimension_name_map: Dict["Dimension", InternalDimension] = {}
        self._mcc_support: Optional[bool] = None
        self._lock_time = None
        self._shallow_load()

    def _shallow_load(self):
        try:
            self._load_level_dat()
        except:
            pass

    def _load_level_dat(self):
        """Load the level.dat file and check the image file"""
        if os.path.isfile(os.path.join(self.path, "icon.png")):
            self._world_image_path = os.path.join(self.path, "icon.png")
        else:
            self._world_image_path = self._missing_world_icon
        self.root_tag = nbt.load(os.path.join(self.path, "level.dat"))

    @staticmethod
    def is_valid(path: str) -> bool:
        if not check_all_exist(path, "level.dat"):
            return False

        try:
            level_dat_root = load_leveldat(path)
        except:
            return False

        if "Data" not in level_dat_root:
            return False

        if "FML" in level_dat_root:
            return False

        return True

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"java": (True, True)}

    @property
    def version(self) -> VersionNumberInt:
        """The data version number that the world was last opened in. eg 2578"""
        if self._version == DefaultVersion:
            self._version = self._get_version()
        return self._version

    def _get_version(self) -> VersionNumberInt:
        return (
            self.root_tag.get("Data", nbt.TAG_Compound())
            .get("DataVersion", nbt.TAG_Int(-1))
            .value
        )

    @property
    def root_tag(self) -> nbt.NBTFile:
        """The level.dat data for the level."""
        return self._root_tag

    @root_tag.setter
    def root_tag(self, root_tag: Union[nbt.NBTFile, nbt.TAG_Compound]):
        if isinstance(root_tag, nbt.TAG_Compound):
            self._root_tag = nbt.NBTFile(root_tag)
        elif isinstance(root_tag, nbt.NBTFile):
            self._root_tag = root_tag
        else:
            raise ValueError("root_tag must be a TAG_Compound or NBTFile")

    @property
    def level_name(self) -> str:
        return str(self.root_tag["Data"].get("LevelName", ""))

    @level_name.setter
    def level_name(self, value: str):
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
        return list(self._dimension_name_map.keys())

    def register_dimension(
        self,
        relative_dimension_path: InternalDimension,
        dimension_name: Optional["Dimension"] = None,
    ):
        """
        Register a new dimension.

        :param relative_dimension_path: The relative path to the dimension directory from the world root. "" for the world root.
        :param dimension_name: The name of the dimension shown to the user
        """
        if dimension_name is None:
            dimension_name: "Dimension" = relative_dimension_path

        if relative_dimension_path:
            path = os.path.join(self.path, relative_dimension_path)
        else:
            path = self.path

        if (
            relative_dimension_path not in self._levels
            and dimension_name not in self._dimension_name_map
        ):
            self._levels[relative_dimension_path] = AnvilDimensionManager(
                path, mcc=self._mcc_support
            )
            self._dimension_name_map[dimension_name] = relative_dimension_path

    def _get_interface_key(
        self, raw_chunk_data: Optional[Any] = None
    ) -> Tuple[str, int]:
        if raw_chunk_data:
            return (
                self.platform,
                raw_chunk_data.get("DataVersion", nbt.TAG_Int(-1)).value,
            )
        else:
            return self.max_world_version

    def _reload_world(self):
        # reload the level.dat in case it has changed
        self._load_level_dat()

        # create the session.lock file (this has mostly been lifted from MCEdit)
        self._lock_time = int(time.time() * 1000)
        try:
            with open(os.path.join(self.path, "session.lock"), "wb") as f:
                f.write(struct.pack(">Q", self._lock_time))
                f.flush()
                os.fsync(f.fileno())
        except PermissionError as e:
            raise PermissionError(
                f"Could not access session.lock. The world may be open somewhere else.\n{e}"
            )

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
                if AnvilDimensionManager.level_regex.fullmatch(dir_name) is None:
                    continue
                self.register_dimension(dir_name)

        for dimension_path in glob.glob(
            os.path.join(self.path, "dimensions", "*", "*", "region")
        ):
            dimension_path_split = dimension_path.split(os.sep)
            dimension_name = f"{dimension_path_split[-3]}/{dimension_path_split[-2]}"
            self.register_dimension(
                os.path.dirname(os.path.relpath(dimension_path, self.path)),
                dimension_name,
            )

    def _open(self):
        """Open the database for reading and writing"""
        self._reload_world()

    def _create(self, overwrite: bool, **kwargs):
        if os.path.isdir(self.path):
            if overwrite:
                shutil.rmtree(self.path)
            else:
                raise ObjectWriteError(
                    f"A world already exists at the path {self.path}"
                )
        self._version = self.translation_manager.get_version(
            self.platform, self.version
        ).data_version

        self.root_tag = root = nbt.TAG_Compound()
        root["Data"] = data = nbt.TAG_Compound()
        data["version"] = nbt.TAG_Int(19133)
        data["DataVersion"] = nbt.TAG_Int(self._version)
        data["LastPlayed"] = nbt.TAG_Long(int(time.time() * 1000))
        data["LevelName"] = nbt.TAG_String("World Created By Amulet")

        os.makedirs(self.path, exist_ok=True)
        self.root_tag.save_to(os.path.join(self.path, "level.dat"))
        self._reload_world()

    @property
    def has_lock(self) -> bool:
        if self._has_lock:
            if self._lock_time is None:
                # the world was created not opened
                return True
            try:
                with open(os.path.join(self.path, "session.lock"), "rb") as f:
                    return struct.unpack(">Q", f.read(8))[0] == self._lock_time
            except:
                return False
        return False

    def pre_save_operation(
        self, level: api_level.BaseLevel
    ) -> Generator[float, None, bool]:
        changed_chunks = list(level.chunks.changed_chunks())
        height = self._calculate_height(level, changed_chunks)
        try:
            while True:
                yield next(height) / 2
        except StopIteration as e:
            height_changed = e.value

        light = self._calculate_light(level, changed_chunks)
        try:
            while True:
                yield next(light) / 2
        except StopIteration as e:
            light_changed = e.value

        return height_changed or light_changed

    @staticmethod
    def _calculate_height(
        level: api_level.BaseLevel, chunks: List[DimensionCoordinates]
    ) -> Generator[float, None, bool]:
        """Calculate the height values for chunks."""
        chunk_count = len(chunks)
        # it looks like the game recalculates the height value if not defined.
        # Just delete the stored height values so that they do not get written back.
        # tested as of 1.12.2. This may not be true for older versions.
        changed = False
        for i, (dimension, cx, cz) in enumerate(chunks):
            try:
                chunk = level.get_chunk(cx, cz, dimension)
            except ChunkLoadError:
                pass
            else:
                changed_ = False
                changed_ |= chunk.misc.pop("height_mapC", None) is not None
                changed_ |= chunk.misc.pop("height_map256IA", None) is not None
                if changed_:
                    changed = True
                    chunk.changed = True
            yield i / chunk_count
        return changed

    @staticmethod
    def _calculate_light(
        level: api_level.BaseLevel, chunks: List[DimensionCoordinates]
    ) -> Generator[float, None, bool]:
        """Calculate the height values for chunks."""
        # this is needed for before 1.14
        chunk_count = len(chunks)
        changed = False
        if level.level_wrapper.version < 1934:
            # the version may be less than 1934 but is at least 1924
            # calculate the light values
            pass
            # TODO
        else:
            # the game will recalculate the light levels
            for i, (dimension, cx, cz) in enumerate(chunks):
                try:
                    chunk = level.get_chunk(cx, cz, dimension)
                except ChunkLoadError:
                    pass
                else:
                    changed_ = False
                    changed_ |= chunk.misc.pop("block_light", None) is not None
                    changed_ |= chunk.misc.pop("sky_light", None) is not None
                    if changed_:
                        changed = True
                        chunk.changed = True
                yield i / chunk_count
        return changed

    def _save(self):
        """Save the data back to the disk database"""
        os.makedirs(self.path, exist_ok=True)
        for level in self._levels.values():
            level.save()
        self.root_tag.save_to(os.path.join(self.path, "level.dat"))
        # TODO: save other world data

    def _close(self):
        """Close the disk database"""
        pass

    def unload(self):
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
            raise DimensionDoesNotExist(dimension)

    def all_chunk_coords(
        self, dimension: "Dimension"
    ) -> Generator[ChunkCoordinates, None, None]:
        if self._has_dimension(dimension):
            yield from self._get_dimension(dimension).all_chunk_coords()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return self._has_dimension(dimension) and self._get_dimension(
            dimension
        ).has_chunk(cx, cz)

    def _delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        """Delete a chunk from a given dimension"""
        if self._has_dimension(dimension):
            self._get_dimension(dimension).delete_chunk(cx, cz)

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: "Dimension"):
        self._get_dimension(dimension).put_chunk_data(cx, cz, data)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: "Dimension"
    ) -> nbt.NBTFile:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        return self._get_dimension(dimension).get_chunk_data(cx, cz)

    def all_player_ids(self) -> Generator[str, None, None]:
        """
        Returns a generator of all player ids that are present in the level
        """
        yield from (
            os.path.splitext(pid)[0]
            for pid in (
                os.path.basename(f)
                for f in glob.iglob(os.path.join(self.path, "playerdata", "*.dat"))
            )
        )

    def get_player(self, player_id: str = LOCAL_PLAYER) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        if player_id == LOCAL_PLAYER and "Player" in self.root_tag["Data"]:
            return Player(
                player_id,
                tuple(map(lambda t: t.value, self.root_tag["Data"]["Player"]["Pos"])),
                tuple(
                    map(lambda t: t.value, self.root_tag["Data"]["Player"]["Rotation"])
                ),
            )
        elif player_id == LOCAL_PLAYER:
            raise KeyError("Local player doesn't exist")

        path = os.path.join(self.path, "playerdata", f"{player_id}.dat")
        if not os.path.exists(path):
            raise KeyError(f"Player {player_id} doesn't exist")
        player_nbt = nbt.load(path)
        return Player(
            player_id,
            tuple(map(lambda t: t.value, player_nbt["Pos"])),
            tuple(map(lambda t: t.value, player_nbt["Rotation"])),
        )


if __name__ == "__main__":
    import sys

    world_path = sys.argv[1]
    world = AnvilDimensionManager(world_path)
    chunk = world.get_chunk_data(0, 0)
    print(chunk)
    world.put_chunk_data(0, 0, chunk)
    world.save()
