from __future__ import annotations

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
    NBTLoadError,
    load as load_nbt,
    utf8_escape_decoder,
    utf8_escape_encoder,
)

from amulet.api.chunk import Chunk
from amulet.api.data_types import DimensionID, ChunkCoordinates
from amulet.api.errors import ChunkDoesNotExist
from amulet.level.base_level import RawLevel, RawDimension, LevelFriend
from amulet.utils.signal import Signal

from ._level_dat import BedrockLevelDAT
from ._chunk import ChunkData

if TYPE_CHECKING:
    from ._level import BedrockLevelPrivate

log = logging.getLogger(__name__)

InternalDimension = Optional[int]
PlayerID = Any
RawPlayer = Any
NativeChunk = Any
RawChunk = Any


class ActorCounter:
    _lock: RLock
    _session: int
    _count: int

    def __init__(self):
        self._lock = RLock()
        self._session = -1
        self._count = 0

    @classmethod
    def from_level(cls, level_dat: BedrockLevelDAT):
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
        level_dat.save()

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


class BedrockRawLevelFriend(LevelFriend):
    _r: BedrockRawLevelPrivate

    __slots__ = ("_r",)

    def __init__(
        self, level_data: BedrockLevelPrivate, raw_data: BedrockRawLevelPrivate
    ):
        super().__init__(level_data)
        self._r = raw_data


class BedrockRawDimension(BedrockRawLevelFriend, RawDimension):
    def __init__(
        self,
        level_data: BedrockLevelPrivate,
        raw_data: BedrockRawLevelPrivate,
        internal_dimension: InternalDimension,
        alias: DimensionID,
    ):
        super().__init__(level_data, raw_data)
        self._internal_dimension = internal_dimension
        self._alias = alias

    @property
    def dimension(self) -> DimensionID:
        return self._alias

    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
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
        key = self._chunk_prefix(cx, cz)
        return any(key + tag in self._r.db for tag in (b",", b"v"))

    def delete_chunk(self, cx: int, cz: int):
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
    lock: RLock
    open: bool
    db: Optional[LevelDB]
    dimensions: dict[Union[DimensionID, InternalDimension], BedrockRawDimension]
    dimension_aliases: list[DimensionID, ...]
    actor_counter: Optional[ActorCounter]

    __slots__ = tuple(__annotations__)

    closed = Signal()

    def __init__(self):
        self.lock = RLock()
        self.open = False
        self.db = None
        self.dimensions = {}
        self.dimension_aliases = []
        self.actor_counter = None


class BedrockRawLevel(LevelFriend, RawLevel):
    _l: BedrockLevelPrivate
    _r: BedrockRawLevelPrivate

    __slots__ = tuple(__annotations__)

    def __init__(self, level_data: BedrockLevelPrivate):
        super().__init__(level_data)
        self._l.opened.connect(self._open)
        self._l.closed.connect(self._close)

    def _open(self):
        self._r.db = LevelDB(os.path.join(self._l.level.path, "db"))
        self._r.actor_counter = ActorCounter.from_level(self._l.level_dat)
        self._r.open = True

    def _close(self):
        self._r.dimensions.clear()
        self._r.db.close()
        self._r.db = None

    @property
    def level_db(self) -> LevelDB:
        """
        The leveldb database.
        Changes made to this are made directly to the level.
        """
        if self._r.db is None:
            raise RuntimeError
        return self._r.db

    def _find_dimensions(self):
        with self._r.lock:
            if self._r.dimensions:
                return

            if not self._r.open:
                raise RuntimeError("Level is not open.")

            self._r.dimensions.clear()
            self._r.dimension_aliases.clear()

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
                    ] = BedrockRawDimension(self._l, self._r, dimension, alias)

            register_dimension(None, "minecraft:overworld")
            register_dimension(1, "minecraft:the_nether")
            register_dimension(2, "minecraft:the_end")

            for key in self._r.db.keys():
                if len(key) == 13 and key[12] in [44, 118]:  # "," "v"
                    register_dimension(struct.unpack("<i", key[8:12])[0])

    def dimensions(self) -> Iterable[DimensionID]:
        self._find_dimensions()
        return tuple(self._r.dimension_aliases)

    def get_dimension(
        self, dimension: Union[DimensionID, InternalDimension]
    ) -> BedrockRawDimension:
        self._find_dimensions()
        if dimension not in self._r.dimensions:
            raise RuntimeError("Dimension does not exist")
        return self._r.dimensions[dimension]

    def all_player_ids(self) -> Iterable[PlayerID]:
        raise NotImplementedError

    def has_player(self, player_id: PlayerID) -> bool:
        raise NotImplementedError

    def get_raw_player(self, player_id: PlayerID) -> RawPlayer:
        raise NotImplementedError

    def set_raw_player(self, player_id: PlayerID, player: RawPlayer):
        raise NotImplementedError
