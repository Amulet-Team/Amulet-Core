from __future__ import annotations

import copy
from typing import Iterable, Any, Optional, Union, TYPE_CHECKING
from threading import RLock
import os
import struct
from contextlib import suppress
import logging

from leveldb import LevelDB

from amulet_nbt import (
    NamedTag,
    LongTag,
    StringTag,
    CompoundTag,
    ByteTag,
    ShortTag,
    ReadContext,
    NBTLoadError,
    load as load_nbt,
    utf8_escape_decoder,
    utf8_escape_encoder,
)

from amulet.api.chunk import Chunk
from amulet.api.data_types import (
    DimensionID,
    ChunkCoordinates,
    BiomeType,
    VersionNumberTuple,
)
from amulet.block import Block, UniversalAirBlock
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ChunkDoesNotExist, PlayerDoesNotExist
from amulet.level.base_level import RawLevel, RawDimension, LevelFriend

from ._level_dat import BedrockLevelDAT
from ._chunk import ChunkData

if TYPE_CHECKING:
    from ._level import BedrockLevelPrivate

log = logging.getLogger(__name__)

InternalDimension = Optional[int]
PlayerID = str
RawPlayer = NamedTag
NativeChunk = Any


LOCAL_PLAYER = "~local_player"
OVERWORLD = "minecraft:overworld"
THE_NETHER = "minecraft:the_nether"
THE_END = "minecraft:the_end"

DefaultSelection = SelectionGroup(
    SelectionBox((-30_000_000, 0, -30_000_000), (30_000_000, 256, 30_000_000))
)


class ActorCounter:
    _lock: RLock
    _session: int
    _count: int

    def __init__(self):
        self._lock = RLock()
        self._session = -1
        self._count = 0

    @classmethod
    def from_level(cls, raw: BedrockRawLevel):
        level_dat = raw.level_dat
        session = level_dat.compound.get_long(
            "worldStartCount", LongTag(0xFFFFFFFF)
        ).py_int
        # for some reason this is a signed int stored in a signed long. Manually apply the sign correctly
        session -= (session & 0x80000000) << 1

        # create the counter object and set the session
        counter = ActorCounter()
        counter._session = session

        # increment and write back so there are no conflicts
        session -= 1
        if session < 0:
            session += 0x100000000
        level_dat.compound["worldStartCount"] = LongTag(session)
        raw.level_dat = level_dat

        return counter

    def next(self) -> tuple[int, int]:
        """
        Get the next unique session id and actor counter.
        Session id is usually negative

        :return: Tuple[session id, actor id]
        """
        with self._lock:
            count = self._count
            self._count += 1
        return self._session, count


class BedrockRawLevelFriend:
    _r: BedrockRawLevelPrivate

    __slots__ = ("_r",)

    def __init__(self, raw_data: BedrockRawLevelPrivate):
        self._r = raw_data


class BedrockRawDimension(BedrockRawLevelFriend, RawDimension):
    def __init__(
        self,
        raw_data: BedrockRawLevelPrivate,
        internal_dimension: InternalDimension,
        alias: DimensionID,
        bounds: SelectionGroup,
    ):
        super().__init__(raw_data)
        self._internal_dimension = internal_dimension
        self._alias = alias
        self._bounds = bounds

    @property
    def dimension(self) -> DimensionID:
        return self._alias

    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
        return self._bounds

    def default_block(self) -> Block:
        """The default block for this dimension"""
        return UniversalAirBlock

    def default_biome(self) -> BiomeType:
        """The default biome for this dimension"""
        # todo: is this stored in the data somewhere?
        return {
            OVERWORLD: "universal_minecraft:plains",
            THE_NETHER: "universal_minecraft:nether",
            THE_END: "universal_minecraft:the_end",
        }.get(self.dimension, "universal_minecraft:plains")

    @property
    def internal_dimension(self) -> InternalDimension:
        return self._internal_dimension

    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        if self._r.closed:
            raise RuntimeError("Level is not open")
        if self._internal_dimension is None:
            mask = slice(8, 9)
            key_len = 9
            keys = (b",", b"v")
        else:
            mask = slice(8, 13)
            key_len = 13
            dim = struct.pack("<i", self._internal_dimension)
            keys = (dim + b",", dim + b"v")
        for key in self._r.db.keys():
            if len(key) == key_len and key[mask] in keys:
                yield

    def _chunk_prefix(self, cx: int, cz: int) -> bytes:
        if self._internal_dimension is None:
            return struct.pack("<ii", cx, cz)
        else:
            return struct.pack("<iii", cx, cz, self._internal_dimension)

    def has_chunk(self, cx: int, cz: int) -> bool:
        if self._r.closed:
            raise RuntimeError("Level is not open")
        key = self._chunk_prefix(cx, cz)
        return any(key + tag in self._r.db for tag in (b",", b"v"))

    def delete_chunk(self, cx: int, cz: int):
        if self._r.closed:
            raise RuntimeError("Level is not open")
        if not self.has_chunk(cx, cz):
            return  # chunk does not exists

        db = self._r.db
        prefix = self._chunk_prefix(cx, cz)
        prefix_len = len(prefix)
        iter_end = prefix + b"\xff\xff\xff\xff"
        keys = []
        for key, _ in db.iterate(prefix, iter_end):
            if key[:prefix_len] == prefix and len(key) <= prefix_len + 2:
                keys.append(key)
        for key in keys:
            db.delete(key)

        try:
            digp = db.get(b"digp" + prefix)
        except KeyError:
            pass
        else:
            db.delete(b"digp" + prefix)
            for i in range(0, len(digp) // 8 * 8, 8):
                actor_key = b"actorprefix" + digp[i : i + 8]
                db.delete(actor_key)

    def get_raw_chunk(self, cx: int, cz: int) -> ChunkData:
        """
        Get a dictionary of chunk key extension in bytes to the raw data in the key.
        chunk key extension are the character(s) after <cx><cz>[level] in the key
        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :return:
        :raises:
            ChunkDoesNotExist if the chunk does not exist
        """
        if self._r.closed:
            raise RuntimeError("Level is not open")
        if not self.has_chunk(cx, cz):
            raise ChunkDoesNotExist

        prefix = self._chunk_prefix(cx, cz)
        prefix_len = len(prefix)
        iter_end = prefix + b"\xff\xff\xff\xff"

        chunk_data = ChunkData()
        for key, val in self._r.db.iterate(prefix, iter_end):
            if key[:prefix_len] == prefix and len(key) <= prefix_len + 2:
                chunk_data[key[prefix_len:]] = val

        with suppress(KeyError):
            digp_key = b"digp" + prefix
            digp = self._r.db.get(digp_key)
            chunk_data[
                b"digp"
            ] = b""  # The presence of this key signals to the put method that this should be created and written
            for i in range(0, (len(digp) // 8) * 8, 8):
                actor_key = b"actorprefix" + digp[i : i + 8]
                try:
                    actor_bytes = self._r.db.get(actor_key)
                    actor = load_nbt(
                        actor_bytes,
                        little_endian=True,
                        string_decoder=utf8_escape_decoder,
                    )
                    actor_tag = actor.compound
                except KeyError:
                    log.error(f"Could not find actor {actor_key}. Skipping.")
                except NBTLoadError:
                    log.error(f"Failed to parse actor {actor_key}. Skipping.")
                else:
                    actor_tag.pop("UniqueID", None)
                    internal_components = actor_tag.setdefault(
                        "internalComponents",
                        CompoundTag(
                            EntityStorageKeyComponent=CompoundTag(
                                StorageKey=StringTag()
                            )
                        ),
                    )  # 717
                    if (
                        isinstance(internal_components, CompoundTag)
                        and internal_components
                    ):
                        if "EntityStorageKeyComponent" in internal_components:
                            # it is an entity
                            entity_component = internal_components[
                                "EntityStorageKeyComponent"
                            ]
                            if isinstance(entity_component, CompoundTag):
                                # delete the storage key component
                                if isinstance(
                                    entity_component.get("StorageKey"), StringTag
                                ):
                                    del entity_component["StorageKey"]
                                # if there is no other data then delete internalComponents
                                if (
                                    len(entity_component) == 0
                                    and len(internal_components) == 1
                                ):
                                    del actor_tag["internalComponents"]
                                else:
                                    log.warning(
                                        f"Extra components found {repr(entity_component)}"
                                    )
                            else:
                                log.warning(
                                    f"Unrecognised EntityStorageKeyComponent type {repr(entity_component)}"
                                )

                            chunk_data.entity_actor.append(actor)
                        else:
                            # it is an unknown actor
                            log.warning(
                                f"Actor {actor_key} has an unknown format. Please report this to a developer {repr(internal_components)}"
                            )
                            for k, v in internal_components.items():
                                if isinstance(v, CompoundTag) and isinstance(
                                    v.get("StorageKey"), StringTag
                                ):
                                    v["StorageKey"] = StringTag()
                            chunk_data.unknown_actor.append(actor)
                    else:
                        log.error(
                            f"internalComponents was not valid for actor {actor_key}. Skipping."
                        )
                        continue

        return chunk_data

    def set_raw_chunk(self, cx: int, cz: int, chunk: ChunkData):
        """
        Set the raw data for a chunk
        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :param chunk: The chunk data to set.
        :return:
        """
        if self._r.closed:
            raise RuntimeError("Level is not open")
        key_prefix = self._chunk_prefix(cx, cz)

        batch = {}

        if b"digp" in chunk:
            # if writing the digp key we need to delete all actors pointed to by the old digp key otherwise there will be memory leaks
            digp_key = b"digp" + key_prefix
            try:
                old_digp = self._r.db.get(digp_key)
            except KeyError:
                pass
            else:
                for i in range(0, len(old_digp) // 8 * 8, 8):
                    actor_key = b"actorprefix" + old_digp[i : i + 8]
                    self._r.db.delete(actor_key)

            digp = []

            def add_actor(actor: NamedTag, is_entity: bool):
                if not (
                    isinstance(actor, NamedTag) and isinstance(actor.tag, CompoundTag)
                ):
                    log.error(f"Actor must be a NamedTag[Compound]")
                    return
                actor_tag = actor.compound
                internal_components = actor_tag.setdefault(
                    "internalComponents", CompoundTag()
                )
                if not isinstance(internal_components, CompoundTag):
                    log.error(
                        f"Invalid internalComponents value. Must be Compound. Skipping. {repr(internal_components)}"
                    )
                    return

                if is_entity:
                    entity_storage = internal_components.setdefault(
                        "EntityStorageKeyComponent", CompoundTag()
                    )
                    if not isinstance(entity_storage, CompoundTag):
                        log.error(
                            f"Invalid EntityStorageKeyComponent value. Must be Compound. Skipping. {repr(entity_storage)}"
                        )
                        return
                    storages = [entity_storage]
                else:
                    storages = []
                    for storage in internal_components.values():
                        if (
                            isinstance(storage, CompoundTag)
                            and storage.get("StorageKey") == StringTag()
                        ):
                            storages.append(storage)
                    if not storages:
                        log.error(
                            f"No valid StorageKeyComponent to write in for unknown actor {internal_components}"
                        )
                        return

                session, uid = self._r.actor_counter.next()
                # session is already negative
                key = struct.pack(">ii", -session, uid)
                # b'\x00\x00\x00\x01\x00\x00\x00\x0c' 1, 12
                for storage in storages:
                    storage["StorageKey"] = StringTag(utf8_escape_decoder(key))
                # -4294967284 ">q" b'\xff\xff\xff\xff\x00\x00\x00\x0c' ">ii" -1, 12
                actor_tag["UniqueID"] = LongTag(
                    struct.unpack(">q", struct.pack(">ii", session, uid))[0]
                )

                batch[b"actorprefix" + key] = actor.save_to(
                    little_endian=True,
                    compressed=False,
                    string_encoder=utf8_escape_encoder,
                )
                digp.append(key)

            for actor_ in chunk.entity_actor:
                add_actor(actor_, True)

            for actor_ in chunk.unknown_actor:
                add_actor(actor_, False)

            del chunk[b"digp"]
            batch[digp_key] = b"".join(digp)

        for key, val in chunk.items():
            key = key_prefix + key
            if val is None:
                self._r.db.delete(key)
            else:
                batch[key] = val
        if batch:
            self._r.db.putBatch(batch)

    def get_native_chunk(self, cx: int, cz: int) -> NativeChunk:
        raise NotImplementedError

    def set_native_chunk(self, cx: int, cz: int, chunk: NativeChunk):
        raise NotImplementedError

    def get_universal_chunk(self, cx: int, cz: int) -> Chunk:
        raise NotImplementedError

    def set_universal_chunk(self, cx: int, cz: int, chunk: Chunk):
        raise NotImplementedError

    def raw_to_native_chunk(self, chunk: ChunkData) -> NativeChunk:
        raise NotImplementedError

    def native_to_raw_chunk(self, chunk: NativeChunk) -> ChunkData:
        raise NotImplementedError

    def native_to_universal_chunk(self, chunk: NativeChunk) -> Chunk:
        raise NotImplementedError

    def universal_to_native_chunk(self, chunk: Chunk) -> NativeChunk:
        raise NotImplementedError


class BedrockRawLevelPrivate:
    # _raw_ref: Callable[[], Optional[BedrockRawLevel]]
    lock: RLock
    closed: bool
    db: Optional[LevelDB]
    dimensions: dict[Union[DimensionID, InternalDimension], BedrockRawDimension]
    dimension_aliases: frozenset[DimensionID]
    actor_counter: Optional[ActorCounter]

    __slots__ = tuple(__annotations__)

    def __init__(self):
        self.lock = RLock()
        self.closed = False
        self.db = None
        self.dimensions = {}
        self.dimension_aliases = frozenset()
        self.actor_counter = None

    # @property
    # def raw(self) -> BedrockRawLevel:
    #     raw = self._raw_ref()
    #     if raw is None:
    #         raise RuntimeError("Raw instance does not exist.")
    #     return raw


class BedrockRawLevel(LevelFriend, RawLevel):
    _l: BedrockLevelPrivate
    _r: Optional[BedrockRawLevelPrivate]
    _level_dat: BedrockLevelDAT

    __slots__ = tuple(__annotations__)

    def __init__(self, level_data: BedrockLevelPrivate):
        super().__init__(level_data)
        self._r = None
        self._l.opened.connect(self._open)
        self._l.closed.connect(self._close)
        self._l.reloaded.connect(self._reload)

    def _reload(self):
        self.level_dat = BedrockLevelDAT.from_file(
            os.path.join(self._l.path, "level.dat")
        )

    def _open(self):
        self._r = BedrockRawLevelPrivate()
        self._r.db = LevelDB(os.path.join(self._l.level.path, "db"))
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
        self._r.actor_counter = ActorCounter.from_level(self)

    def _close(self):
        self._r.closed = True
        self._r.db.close()
        self._r = None

    @property
    def level_db(self) -> LevelDB:
        """
        The leveldb database.
        Changes made to this are made directly to the level.
        """
        if self._r is None:
            raise RuntimeError("Level is not open")
        return self._r.db

    @property
    def level_dat(self) -> BedrockLevelDAT:
        """Get the level.dat file for the world"""
        return copy.deepcopy(self.level_dat)

    @level_dat.setter
    def level_dat(self, level_dat: BedrockLevelDAT):
        if not isinstance(level_dat, BedrockLevelDAT):
            raise TypeError
        self.level_dat = level_dat = copy.deepcopy(level_dat)
        level_dat.save_to(os.path.join(self._l.level.path, "level.dat"))

    @property
    def max_game_version(self) -> VersionNumberTuple:
        """
        The game version that the level was last opened in.
        This is used to determine the data format to save in.
        """
        try:
            return tuple(
                t.py_int
                for t in self.level_dat.compound.get_list("lastOpenedWithVersion")
            )
        except Exception:
            return 1, 2, 0

    @property
    def last_played(self) -> int:
        try:
            return self.level_dat.compound.get_long("LastPlayed", LongTag()).py_int
        except Exception:
            return 0

    def _find_dimensions(self):
        if self._r is None:
            raise RuntimeError("Level is not open")
        if self._r.dimensions:
            return
        with self._r.lock:
            if self._r.dimensions:
                return

            dimenion_bounds = {}

            # find dimension bounds
            experiments = self.level_dat.compound.get_compound(
                "experiments", CompoundTag()
            )
            if (
                experiments.get_byte("caves_and_cliffs", ByteTag()).py_int
                or experiments.get_byte("caves_and_cliffs_internal", ByteTag()).py_int
                or self.max_game_version >= (1, 18)
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
            ):
                """
                Register a new dimension.

                :param dimension: The internal representation of the dimension
                :param alias: The name of the level visible to the user. Defaults to f"DIM{dimension}"
                :return:
                """
                if dimension not in self._r.dimensions:
                    if alias is None:
                        alias = f"DIM{dimension}"
                    self._r.dimensions[dimension] = self._r.dimensions[
                        alias
                    ] = BedrockRawDimension(
                        self._r,
                        dimension,
                        alias,
                        dimenion_bounds.get(alias, DefaultSelection),
                    )
                    dimensions.add(alias)

            register_dimension(None, OVERWORLD)
            register_dimension(1, THE_NETHER)
            register_dimension(2, THE_END)

            for key in self._r.db.keys():
                if len(key) == 13 and key[12] in [44, 118]:  # "," "v"
                    register_dimension(struct.unpack("<i", key[8:12])[0])

            self._r.dimension_aliases = frozenset(dimensions)

    def dimensions(self) -> frozenset[DimensionID]:
        self._find_dimensions()
        return self._r.dimension_aliases

    def get_dimension(
        self, dimension: Union[DimensionID, InternalDimension]
    ) -> BedrockRawDimension:
        self._find_dimensions()
        if dimension not in self._r.dimensions:
            raise RuntimeError("Dimension does not exist")
        return self._r.dimensions[dimension]

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

    def set_raw_player(self, player_id: PlayerID, player: RawPlayer):
        raise NotImplementedError
