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
    FloatTag,
    DoubleTag,
    StringTag,
    ListTag,
    CompoundTag,
    NamedTag,
    load as load_nbt,
)
from amulet.player import Player, LOCAL_PLAYER
from amulet.api.chunk import Chunk
from amulet.selection import SelectionGroup, SelectionBox
from amulet.api.wrapper import WorldFormatWrapper, DefaultSelection
from amulet.utils.format_utils import check_all_exist
from amulet.errors import (
    DimensionDoesNotExist,
    LevelWriteError,
    ChunkLoadError,
    ChunkDoesNotExist,
    PlayerDoesNotExist,
)
from amulet.version import PlatformType
from amulet.data_types import ChunkCoordinates
from amulet.api.data_types import (
    VersionNumberInt,
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

    def all_player_ids(self) -> Iterable[str]:
        """
        Returns a generator of all player ids that are present in the level
        """
        for f in glob.iglob(
            os.path.join(glob.escape(self.path), "playerdata", "*.dat")
        ):
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
