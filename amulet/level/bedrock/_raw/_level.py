from __future__ import annotations

import copy
from typing import Optional, Union, TYPE_CHECKING, overload
from collections.abc import Iterable, Mapping, Iterator
from threading import RLock
import os
import struct
import logging

from leveldb import LevelDB

from amulet_nbt import (
    LongTag,
    CompoundTag,
    ByteTag,
    ShortTag,
    ReadContext,
    load as load_nbt,
    utf8_escape_decoder,
)

from amulet.api.data_types import (
    DimensionID,
)
from amulet.selection import SelectionGroup, SelectionBox
from amulet.api.errors import PlayerDoesNotExist
from amulet.level.abc import (
    RawLevel,
    RawLevelPlayerComponent,
    LevelFriend,
)
from amulet.version import SemanticVersion

from ._level_dat import BedrockLevelDAT
from ._actor_counter import ActorCounter
from ._dimension import BedrockRawDimension
from ._constant import OVERWORLD, THE_NETHER, THE_END, LOCAL_PLAYER, DefaultSelection
from ._typing import InternalDimension, PlayerID, RawPlayer

if TYPE_CHECKING:
    from .._level import BedrockLevel

log = logging.getLogger(__name__)


class LegacyBlockIdMap(Mapping[int, tuple[str, str]]):
    def __init__(self) -> None:
        self._str_to_int: dict[tuple[str, str], int] = {}
        self._int_to_str: dict[int, tuple[str, str]] = {}

    def int_to_str(self, index: int) -> tuple[str, str]:
        return self._int_to_str[index]

    def str_to_int(self, block_id: tuple[str, str]) -> int:
        return self._str_to_int[block_id]

    def register(self, index: int, block_id: tuple[str, str]) -> None:
        if block_id in self._str_to_int:
            raise RuntimeError(f"Block id {block_id} has already been registered")
        if index in self._int_to_str:
            raise RuntimeError(f"Block index {index} has already been registered")
        self._str_to_int[block_id] = index
        self._int_to_str[index] = block_id

    @overload
    def __getitem__(self, key: int) -> tuple[str, str]:
        ...

    @overload
    def __getitem__(self, key: tuple[str, str]) -> int:
        ...

    def __getitem__(self, key: int | tuple[str, str]) -> int | tuple[str, str]:
        if isinstance(key, int):
            return self._int_to_str[key]
        else:
            return self._str_to_int[key]

    def __len__(self) -> int:
        return len(self._int_to_str)

    def __iter__(self) -> Iterator[int]:
        yield from self._int_to_str


class BedrockRawLevelOpenData:
    """Data that only exists when the level is open"""

    dimensions: dict[Union[DimensionID, InternalDimension], BedrockRawDimension]
    dimensions_lock: RLock
    db: LevelDB
    dimension_aliases: frozenset[DimensionID]
    actor_counter: ActorCounter
    legacy_block_map: LegacyBlockIdMap

    def __init__(self, db: LevelDB, actor_counter: ActorCounter):
        self.db = db
        self.dimensions = {}
        self.dimensions_lock = RLock()
        self.dimension_aliases = frozenset()
        self.actor_counter = actor_counter
        self.legacy_block_map = LegacyBlockIdMap()


class BedrockRawLevel(
    LevelFriend[BedrockLevel],
    RawLevel,
    RawLevelPlayerComponent[PlayerID, RawPlayer],
):
    _level_dat: BedrockLevelDAT
    _o_data: BedrockRawLevelOpenData | None

    __slots__ = tuple(__annotations__)

    def __init__(self, level: BedrockLevel) -> None:
        super().__init__(level)
        self._o_data = None

    @property
    def _o(self) -> BedrockRawLevelOpenData:
        o = self._o_data
        if o is None:
            raise RuntimeError("The level is not open.")
        return o

    def _reload(self) -> None:
        self.level_dat = BedrockLevelDAT.from_file(
            os.path.join(self._l.path, "level.dat")
        )

    def _open(self) -> None:
        db = LevelDB(os.path.join(self._l.path, "db"))
        actor_counter = ActorCounter.from_level(self)
        self._o_data = BedrockRawLevelOpenData(db, actor_counter)

        # TODO: implement error handling and level closing if the db errors
        # except LevelDBEncrypted as e:
        #     self._is_open = self._has_lock = False
        #     raise LevelDBException(
        #         "It looks like this world is from the marketplace.\nThese worlds are encrypted and cannot be edited."
        #     ) from e
        # except LevelDBException as e:
        #     msg = str(e)
        #     self._is_open = self._has_lock = False
        #     # I don't know if there is a better way of handling this.
        #     if msg.startswith("IO error:") and msg.endswith(": Permission denied"):
        #         traceback.print_exc()
        #         raise LevelDBException(
        #             f"Failed to load the database. The world may be open somewhere else.\n{msg}"
        #         ) from e
        #     else:
        #         raise e

    def _close(self) -> None:
        open_data = self._o
        self._o_data = None
        open_data.db.close()
        for dimension in open_data.dimensions.values():
            dimension._invalidate_r()

    @property
    def level_db(self) -> LevelDB:
        """
        The leveldb database.
        Changes made to this are made directly to the level.
        """
        return self._o.db

    @property
    def level_dat(self) -> BedrockLevelDAT:
        """Get the level.dat file for the world"""
        return copy.deepcopy(self._level_dat)

    @level_dat.setter
    def level_dat(self, level_dat: BedrockLevelDAT) -> None:
        if not isinstance(level_dat, BedrockLevelDAT):
            raise TypeError
        self.level_dat = level_dat = copy.deepcopy(level_dat)
        level_dat.save_to(os.path.join(self._l.path, "level.dat"))

    @property
    def max_game_version(self) -> SemanticVersion:
        """
        The game version that the level was last opened in.
        This is used to determine the data format to save in.
        """
        try:
            return SemanticVersion(
                "bedrock",
                tuple(
                    t.py_int
                    for t in self.level_dat.compound.get_list("lastOpenedWithVersion")
                ),
            )
        except Exception:
            return SemanticVersion("bedrock", (1, 2, 0))

    @property
    def last_played(self) -> int:
        try:
            return self.level_dat.compound.get_long("LastPlayed", LongTag()).py_int
        except Exception:
            return 0

    def _find_dimensions(self) -> None:
        if self._o.dimensions:
            return
        with self._o.dimensions_lock:
            if self._o.dimensions:
                return

            dimenion_bounds = {}

            # find dimension bounds
            experiments = self.level_dat.compound.get_compound(
                "experiments", CompoundTag()
            )
            if (
                experiments.get_byte("caves_and_cliffs", ByteTag()).py_int
                or experiments.get_byte("caves_and_cliffs_internal", ByteTag()).py_int
                or self.max_game_version.semantic_version >= (1, 18)
            ):
                dimenion_bounds[OVERWORLD] = SelectionGroup(
                    SelectionBox(
                        (-30_000_000, -64, -30_000_000), (30_000_000, 320, 30_000_000)
                    )
                )
            else:
                dimenion_bounds[OVERWORLD] = DefaultSelection
            dimenion_bounds[THE_NETHER] = SelectionGroup(
                SelectionBox(
                    (-30_000_000, 0, -30_000_000), (30_000_000, 128, 30_000_000)
                )
            )
            dimenion_bounds[THE_END] = DefaultSelection

            if b"LevelChunkMetaDataDictionary" in self.level_db:
                data = self.level_db[b"LevelChunkMetaDataDictionary"]
                count, data = struct.unpack("<I", data[:4])[0], data[4:]
                for _ in range(count):
                    key, data = data[:8], data[8:]
                    context = ReadContext()
                    value = load_nbt(
                        data,
                        little_endian=True,
                        compressed=False,
                        string_decoder=utf8_escape_decoder,
                        read_context=context,
                    ).compound
                    data = data[context.offset :]

                    try:
                        dimension_name = value.get_string("DimensionName").py_str
                        # The dimension names are stored differently TODO: split local and global names
                        dimension_name = {
                            "Overworld": OVERWORLD,
                            "Nether": THE_NETHER,
                            "TheEnd": THE_END,
                        }.get(dimension_name, dimension_name)

                    except KeyError:
                        # Some entries seem to not have a dimension assigned to them. Is there a default? We will skip over these for now.
                        # {'LastSavedBaseGameVersion': StringTag("1.19.81"), 'LastSavedDimensionHeightRange': CompoundTag({'max': ShortTag(320), 'min': ShortTag(-64)})}
                        pass
                    else:
                        previous_bounds = dimenion_bounds.get(
                            dimension_name, DefaultSelection
                        )
                        min_y = min(
                            value.get_compound(
                                "LastSavedDimensionHeightRange", CompoundTag()
                            )
                            .get_short("min", ShortTag())
                            .py_int,
                            value.get_compound(
                                "OriginalDimensionHeightRange", CompoundTag()
                            )
                            .get_short("min", ShortTag())
                            .py_int,
                            previous_bounds.min_y,
                        )
                        max_y = max(
                            value.get_compound(
                                "LastSavedDimensionHeightRange", CompoundTag()
                            )
                            .get_short("max", ShortTag())
                            .py_int,
                            value.get_compound(
                                "OriginalDimensionHeightRange", CompoundTag()
                            )
                            .get_short("max", ShortTag())
                            .py_int,
                            previous_bounds.max_y,
                        )
                        dimenion_bounds[dimension_name] = SelectionGroup(
                            SelectionBox(
                                (previous_bounds.min_x, min_y, previous_bounds.min_z),
                                (previous_bounds.max_x, max_y, previous_bounds.max_z),
                            )
                        )

            dimensions = set()

            def register_dimension(
                dimension: InternalDimension, alias: Optional[str] = None
            ) -> None:
                """
                Register a new dimension.

                :param dimension: The internal representation of the dimension
                :param alias: The name of the level visible to the user. Defaults to f"DIM{dimension}"
                :return:
                """
                if dimension not in self._o.dimensions:
                    if alias is None:
                        alias = f"DIM{dimension}"
                    self._o.dimensions[dimension] = self._o.dimensions[
                        alias
                    ] = BedrockRawDimension(
                        self,
                        dimension,
                        alias,
                        dimenion_bounds.get(alias, DefaultSelection),
                    )
                    dimensions.add(alias)

            register_dimension(None, OVERWORLD)
            register_dimension(1, THE_NETHER)
            register_dimension(2, THE_END)

            for key in self._o.db.keys():
                if len(key) == 13 and key[12] in [44, 118]:  # "," "v"
                    register_dimension(struct.unpack("<i", key[8:12])[0])

            self._o.dimension_aliases = frozenset(dimensions)

    def dimensions(self) -> frozenset[DimensionID]:
        self._find_dimensions()
        return self._o.dimension_aliases

    def get_dimension(
        self, dimension: Union[DimensionID, InternalDimension]
    ) -> BedrockRawDimension:
        self._find_dimensions()
        if dimension not in self._o.dimensions:
            raise RuntimeError(f"Dimension {dimension} does not exist")
        return self._o.dimensions[dimension]

    def players(self) -> Iterable[PlayerID]:
        yield from (
            pid[7:].decode("utf-8")
            for pid, _ in self.level_db.iterate(b"player_", b"player_\xFF")
        )
        if self.has_player(LOCAL_PLAYER):
            yield LOCAL_PLAYER

    def has_player(self, player_id: PlayerID) -> bool:
        if player_id != LOCAL_PLAYER:
            player_id = f"player_{player_id}"
        return player_id.encode("utf-8") in self.level_db

    def get_raw_player(self, player_id: PlayerID) -> RawPlayer:
        if player_id == LOCAL_PLAYER:
            key = player_id.encode("utf-8")
        else:
            key = f"player_{player_id}".encode("utf-8")
        try:
            data = self.level_db.get(key)
        except KeyError:
            raise PlayerDoesNotExist(f"Player {player_id} doesn't exist")
        return load_nbt(
            data,
            compressed=False,
            little_endian=True,
            string_decoder=utf8_escape_decoder,
        )

    def set_raw_player(self, player_id: PlayerID, player: RawPlayer) -> None:
        raise NotImplementedError

    @property
    def legacy_block_map(self) -> LegacyBlockIdMap:
        """A two-way map from legacy block id <-> block string"""
        return self._o.legacy_block_map
