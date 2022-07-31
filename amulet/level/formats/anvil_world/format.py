from __future__ import annotations

import os
import struct
from typing import (
    Tuple,
    Dict,
    Generator,
    Optional,
    List,
    Union,
    Iterable,
    BinaryIO,
    Any,
)
import time
import glob
import shutil
import json
import logging

import portalocker

from amulet_nbt import (
    IntTag,
    LongTag,
    DoubleTag,
    StringTag,
    ListTag,
    CompoundTag,
    NamedTag,
    load as load_nbt,
)
from amulet.api.player import Player, LOCAL_PLAYER
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.wrapper import WorldFormatWrapper, DefaultSelection
from amulet.utils.format_utils import check_all_exist
from amulet.api.errors import (
    DimensionDoesNotExist,
    ObjectWriteError,
    ChunkLoadError,
    ChunkDoesNotExist,
    PlayerDoesNotExist,
)
from amulet.api.data_types import (
    ChunkCoordinates,
    VersionNumberInt,
    PlatformType,
    DimensionCoordinates,
    AnyNDArray,
    Dimension,
)
from .dimension import AnvilDimensionManager, ChunkDataType
from amulet.api import level as api_level
from amulet.level.interfaces.chunk.anvil.base_anvil_interface import BaseAnvilInterface
from .data_pack import DataPack, DataPackManager

log = logging.getLogger(__name__)

InternalDimension = str
OVERWORLD = "minecraft:overworld"
THE_NETHER = "minecraft:the_nether"
THE_END = "minecraft:the_end"


class AnvilFormat(WorldFormatWrapper[VersionNumberInt]):
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
        self._root_tag: NamedTag = NamedTag()
        self._levels: Dict[InternalDimension, AnvilDimensionManager] = {}
        self._dimension_name_map: Dict[Dimension, InternalDimension] = {}
        self._mcc_support: Optional[bool] = None
        self._lock_time: Optional[bytes] = None
        self._lock: Optional[BinaryIO] = None
        self._data_pack: Optional[DataPackManager] = None
        self._shallow_load()

    def __del__(self):
        self.close()

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
        self.root_tag = load_nbt(os.path.join(self.path, "level.dat"))

    @staticmethod
    def is_valid(path: str) -> bool:
        if not check_all_exist(path, "level.dat"):
            return False

        try:
            level_dat_root = load_nbt(os.path.join(path, "level.dat")).compound
        except:
            return False

        return "Data" in level_dat_root and "FML" not in level_dat_root

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"java": (True, True)}

    @property
    def version(self) -> VersionNumberInt:
        """The data version number that the world was last opened in. eg 2578"""
        if self._version is None:
            self._version = self._get_version()
        return self._version

    def _get_version(self) -> VersionNumberInt:
        return (
            self.root_tag.compound.get_compound("Data", CompoundTag())
            .get_int("DataVersion", IntTag(-1))
            .py_int
        )

    @property
    def root_tag(self) -> NamedTag:
        """The level.dat data for the level."""
        return self._root_tag

    @root_tag.setter
    def root_tag(self, root_tag: Union[NamedTag, CompoundTag]):
        if isinstance(root_tag, CompoundTag):
            self._root_tag = NamedTag(root_tag)
        elif isinstance(root_tag, NamedTag):
            self._root_tag = root_tag
        else:
            raise ValueError("root_tag must be a CompoundTag or NamedTag")

    @property
    def level_name(self) -> str:
        return (
            self.root_tag.compound.get_compound("Data").get_string("LevelName").py_str
        )

    @level_name.setter
    def level_name(self, value: str):
        self.root_tag.compound.setdefault_compound("Data")["LevelName"] = StringTag(
            value
        )

    @property
    def last_played(self) -> int:
        return (
            self.root_tag.compound.get_compound("Data").get_long("LastPlayed").py_int
            // 1000
        )

    @property
    def game_version_string(self) -> str:
        try:
            return f'Java {self.root_tag.compound.get_compound("Data").get_compound("Version").get_string("Name").py_str}'
        except Exception:
            return f"Java Unknown Version"

    @property
    def data_pack(self) -> DataPackManager:
        if self._data_pack is None:
            packs = []
            enabled_packs = (
                self.root_tag.compound.get_compound("Data")
                .get_compound("DataPacks", CompoundTag())
                .get_list("Enabled", ListTag())
            )
            for pack in enabled_packs:
                if isinstance(pack, StringTag):
                    pack_name: str = pack.py_str
                    if pack_name == "vanilla":
                        pass
                    elif pack_name.startswith("file/"):
                        path = os.path.join(self.path, "datapacks", pack_name[5:])
                        if DataPack.is_path_valid(path):
                            packs.append(DataPack(path))
            self._data_pack = DataPackManager(packs)
        return self._data_pack

    @property
    def dimensions(self) -> List[Dimension]:
        return list(self._dimension_name_map.keys())

    def _register_dimension(
        self,
        relative_dimension_path: InternalDimension,
        dimension_name: Optional[Dimension] = None,
    ):
        """
        Register a new dimension.

        :param relative_dimension_path: The relative path to the dimension directory from the world root. "" for the world root.
        :param dimension_name: The name of the dimension shown to the user
        """
        if dimension_name is None:
            dimension_name: Dimension = relative_dimension_path

        if relative_dimension_path:
            path = os.path.join(self.path, relative_dimension_path)
        else:
            path = self.path

        if (
            relative_dimension_path not in self._levels
            and dimension_name not in self._dimension_name_map
        ):
            self._levels[relative_dimension_path] = AnvilDimensionManager(
                path,
                mcc=self._mcc_support,
                layers=("region",) + ("entities",) * (self.version >= 2681),
            )
            self._dimension_name_map[dimension_name] = relative_dimension_path
            bounds = DefaultSelection
            if self.version >= 2709:  # This number might be smaller
                dimension_settings = (
                    self.root_tag.compound.get_compound("Data", CompoundTag())
                    .get_compound("WorldGenSettings", CompoundTag())
                    .get_compound("dimensions", CompoundTag())
                    .get_compound(dimension_name, CompoundTag())
                )
                dimension_tag = dimension_settings.get("type")
                if isinstance(dimension_tag, StringTag):
                    # the settings are in the data pack
                    dimension_name = dimension_tag.py_str
                    if ":" in dimension_name:
                        namespace, base_name = dimension_name.split(":", 1)
                        if (
                            self.version >= 2834
                            and namespace == "minecraft"
                            and base_name == "overworld"
                        ):
                            bounds = SelectionGroup(
                                SelectionBox(
                                    (-30_000_000, -64, -30_000_000),
                                    (30_000_000, 320, 30_000_000),
                                )
                            )
                        dimension_path = (
                            f"data/{namespace}/dimension_type/{base_name}.json"
                        )
                        if self.data_pack.has_file(dimension_path):
                            with self.data_pack.open(dimension_path) as d:
                                try:
                                    dimension_settings_json = json.load(d)
                                except json.JSONDecodeError:
                                    pass
                                else:
                                    if (
                                        "min_y" in dimension_settings_json
                                        and isinstance(
                                            dimension_settings_json["min_y"], int
                                        )
                                    ):
                                        min_y = dimension_settings_json["min_y"]
                                        if min_y % 16:
                                            min_y = 16 * (min_y // 16)
                                    else:
                                        min_y = 0
                                    if (
                                        "height" in dimension_settings_json
                                        and isinstance(
                                            dimension_settings_json["height"], int
                                        )
                                    ):
                                        height = dimension_settings_json["height"]
                                        if height % 16:
                                            height = -16 * (-height // 16)
                                    else:
                                        height = 256

                                    bounds = SelectionGroup(
                                        SelectionBox(
                                            (-30_000_000, min_y, -30_000_000),
                                            (30_000_000, min_y + height, 30_000_000),
                                        )
                                    )

                elif isinstance(dimension_tag, CompoundTag):
                    # the settings are here
                    dimension_compound_tag = dimension_tag
                    min_y = (
                        dimension_compound_tag.get_int("min_y", IntTag()).py_int // 16
                    ) * 16
                    height = (
                        -dimension_compound_tag.get_int("height", IntTag(256)).py_int
                        // 16
                    ) * -16
                    bounds = SelectionGroup(
                        SelectionBox(
                            (-30_000_000, min_y, -30_000_000),
                            (30_000_000, min_y + height, 30_000_000),
                        )
                    )
                else:
                    log.error(
                        f"Expected dimension_tag to be a StringTag or CompoundTag. Got {repr(dimension_tag)} for dimension {dimension_name}"
                    )

            self._bounds[dimension_name] = bounds

    def _get_interface(self, raw_chunk_data: Optional[Any] = None) -> "Interface":
        from amulet.level.loader import Interfaces

        key = self._get_interface_key(raw_chunk_data)
        return Interfaces.get(key)

    def _get_interface_key(
        self, raw_chunk_data: Optional[ChunkDataType] = None
    ) -> Tuple[str, int]:
        if raw_chunk_data is None:
            return self.max_world_version
        else:
            return (
                self.platform,
                raw_chunk_data.get("region", NamedTag())
                .compound.get_int("DataVersion", IntTag(-1))
                .py_int,
            )

    def _decode(
        self,
        interface: BaseAnvilInterface,
        dimension: Dimension,
        cx: int,
        cz: int,
        raw_chunk_data: ChunkDataType,
    ) -> Tuple[Chunk, AnyNDArray]:
        bounds = self.bounds(dimension).bounds
        return interface.decode(cx, cz, raw_chunk_data, (bounds[0][1], bounds[1][1]))

    def _encode(
        self,
        interface: BaseAnvilInterface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
    ) -> ChunkDataType:
        bounds = self.bounds(dimension).bounds
        return interface.encode(
            chunk, chunk_palette, self.max_world_version, (bounds[0][1], bounds[1][1])
        )

    def _reload_world(self):
        # reload the level.dat in case it has changed
        self._load_level_dat()

        # create the session.lock file (this has mostly been lifted from MCEdit)
        try:
            # open the file for writing and reading and lock it
            self._lock = open(os.path.join(self.path, "session.lock"), "wb+")
            portalocker.lock(self._lock, portalocker.LockFlags.EXCLUSIVE)

            # write the current time to the file
            self._lock_time = struct.pack(">Q", int(time.time() * 1000))
            self._lock.write(self._lock_time)

            # flush the changes to disk
            self._lock.flush()
            os.fsync(self._lock.fileno())

        except Exception as e:
            self._lock_time = None
            if self._lock is not None:
                self._lock.close()
                self._lock = None

            self._is_open = False
            self._has_lock = False
            raise Exception(
                f"Could not access session.lock. The world may be open somewhere else.\n{e}"
            ) from e

        self._is_open = True
        self._has_lock = True

        # the real number might actually be lower
        self._mcc_support = self.version > 2203

        self._levels.clear()
        self._bounds.clear()

        # load all the levels
        self._register_dimension("", OVERWORLD)
        self._register_dimension("DIM-1", THE_NETHER)
        self._register_dimension("DIM1", THE_END)

        for dir_name in os.listdir(self.path):
            level_path = os.path.join(self.path, dir_name)
            if os.path.isdir(level_path) and dir_name.startswith("DIM"):
                if AnvilDimensionManager.level_regex.fullmatch(dir_name) is None:
                    continue
                self._register_dimension(dir_name)

        for dimension_path in glob.glob(
            os.path.join(self.path, "dimensions", "*", "*", "region")
        ):
            dimension_path_split = dimension_path.split(os.sep)
            dimension_name = f"{dimension_path_split[-3]}:{dimension_path_split[-2]}"
            self._register_dimension(
                os.path.dirname(os.path.relpath(dimension_path, self.path)),
                dimension_name,
            )

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
        self._version = self.translation_manager.get_version(
            self.platform, self.version
        ).data_version

        self.root_tag = root = CompoundTag()
        root["Data"] = data = CompoundTag()
        data["version"] = IntTag(19133)
        data["DataVersion"] = IntTag(self._version)
        data["LastPlayed"] = LongTag(int(time.time() * 1000))
        data["LevelName"] = StringTag("World Created By Amulet")

        os.makedirs(self.path, exist_ok=True)
        self.root_tag.save_to(os.path.join(self.path, "level.dat"))
        self._reload_world()

    @property
    def has_lock(self) -> bool:
        if self._has_lock:
            self._lock.seek(0)
            return self._lock.read(8) == self._lock_time
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

        # light = self._calculate_light(level, changed_chunks)
        # try:
        #     while True:
        #         yield next(light) / 2
        # except StopIteration as e:
        #     light_changed = e.value

        return height_changed  # or light_changed

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
        if self._lock is not None:
            portalocker.unlock(self._lock)
            self._lock.close()

    def unload(self):
        for level in self._levels.values():
            level.unload()

    def _has_dimension(self, dimension: Dimension):
        return (
            dimension in self._dimension_name_map
            and self._dimension_name_map[dimension] in self._levels
        )

    def _get_dimension(self, dimension: Dimension):
        self._verify_has_lock()
        if self._has_dimension(dimension):
            return self._levels[self._dimension_name_map[dimension]]
        else:
            raise DimensionDoesNotExist(dimension)

    def all_chunk_coords(self, dimension: Dimension) -> Iterable[ChunkCoordinates]:
        if self._has_dimension(dimension):
            yield from self._get_dimension(dimension).all_chunk_coords()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return self._has_dimension(dimension) and self._get_dimension(
            dimension
        ).has_chunk(cx, cz)

    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        """Delete a chunk from a given dimension"""
        if self._has_dimension(dimension):
            self._get_dimension(dimension).delete_chunk(cx, cz)

    # TODO: add a new version of this method that handles all the raw data
    def put_raw_chunk_data(
        self, cx: int, cz: int, data: NamedTag, dimension: Dimension
    ):
        """
        Commit the raw chunk data to the FormatWrapper cache.

        Call :meth:`save` to push all the cache data to the level.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param data: The raw data to commit to the level.
        :param dimension: The dimension to load the data from.
        """
        self._verify_has_lock()
        self._put_raw_chunk_data(cx, cz, {"region": data}, dimension)

    def _put_raw_chunk_data(
        self, cx: int, cz: int, data: ChunkDataType, dimension: Dimension
    ):
        self._get_dimension(dimension).put_chunk_data_layers(cx, cz, data)

    # TODO: add a new version of this method that handles all the raw data
    def get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> NamedTag:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        # TODO: make this return layer data
        return self._safe_load(
            self._legacy_get_raw_chunk_data,
            (cx, cz, dimension),
            "Error loading chunk {} {} {}",
            ChunkLoadError,
            ChunkDoesNotExist,
        )

    def _legacy_get_raw_chunk_data(
        self, cx: int, cz: int, dimension: Dimension
    ) -> NamedTag:
        layers = self._get_raw_chunk_data(cx, cz, dimension)
        if "region" in layers:
            return layers["region"]
        else:
            raise ChunkDoesNotExist

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: Dimension
    ) -> ChunkDataType:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        return self._get_dimension(dimension).get_chunk_data_layers(cx, cz)

    def all_player_ids(self) -> Iterable[str]:
        """
        Returns a generator of all player ids that are present in the level
        """
        for f in glob.iglob(os.path.join(self.path, "playerdata", "*.dat")):
            yield os.path.splitext(os.path.basename(f))[0]
        if self.has_player(LOCAL_PLAYER):
            yield LOCAL_PLAYER

    def has_player(self, player_id: str) -> bool:
        if player_id == LOCAL_PLAYER:
            return "Player" in self.root_tag.compound.get_compound("Data")
        else:
            return os.path.isfile(
                os.path.join(self.path, "playerdata", f"{player_id}.dat")
            )

    def _load_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        player_nbt = self._get_raw_player_data(player_id)
        dimension = player_nbt["Dimension"]
        # TODO: rework this when there is better dimension support.
        if isinstance(dimension, IntTag):
            if -1 <= dimension.py_int <= 1:
                dimension_str = {-1: THE_NETHER, 0: OVERWORLD, 1: THE_END}[
                    dimension.py_int
                ]
            else:
                dimension_str = f"DIM{dimension}"
        elif isinstance(dimension, StringTag):
            dimension_str = dimension.py_str
        else:
            dimension_str = OVERWORLD
        if dimension_str not in self._dimension_name_map:
            dimension_str = OVERWORLD

        # get the players position
        pos_data = player_nbt.get("Pos")
        if (
            isinstance(pos_data, ListTag)
            and len(pos_data) == 3
            and pos_data.list_data_type == DoubleTag.tag_id
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
            and rot_data.list_data_type == DoubleTag.tag_id
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

    def _get_raw_player_data(self, player_id: str) -> CompoundTag:
        if player_id == LOCAL_PLAYER:
            if "Player" in self.root_tag.compound.get_compound("Data"):
                return self.root_tag.compound.get_compound("Data").get_compound(
                    "Player"
                )
            else:
                raise PlayerDoesNotExist("Local player doesn't exist")
        else:
            path = os.path.join(self.path, "playerdata", f"{player_id}.dat")
            if os.path.exists(path):
                return load_nbt(path).compound
            raise PlayerDoesNotExist(f"Player {player_id} does not exist")


if __name__ == "__main__":
    import sys

    world_path = sys.argv[1]
    world = AnvilDimensionManager(world_path)
    chunk_ = world.get_chunk_data(0, 0)
    print(chunk_)
    world.put_chunk_data(0, 0, chunk_)
    world.save()
