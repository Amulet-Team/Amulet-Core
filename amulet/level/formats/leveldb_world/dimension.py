from __future__ import annotations

import struct
from typing import (
    Dict,
    Set,
    Optional,
    List,
    TYPE_CHECKING,
    Tuple,
    Union,
)
from threading import RLock
import logging
from contextlib import suppress

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

from amulet.api.errors import ChunkDoesNotExist, DimensionDoesNotExist
from amulet.api.data_types import ChunkCoordinates
from amulet.libs.leveldb import LevelDB
from .chunk import ChunkData

if TYPE_CHECKING:
    from amulet.api.data_types import Dimension
    from .format import LevelDBFormat

log = logging.getLogger(__name__)

InternalDimension = Optional[int]
OVERWORLD = "minecraft:overworld"
THE_NETHER = "minecraft:the_nether"
THE_END = "minecraft:the_end"


class ActorCounter:
    _lock: RLock
    _session: int
    _count: int

    def __init__(self):
        self._lock = RLock()
        self._session = -1
        self._count = 0

    @classmethod
    def from_level(cls, level: LevelDBFormat):
        session = level.root_tag.compound.get_long(
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
        level.root_tag.compound["worldStartCount"] = LongTag(session)
        level.root_tag.save()

        return counter

    def next(self) -> Tuple[int, int]:
        """
        Get the next unique session id and actor counter.
        Session id is usually negative

        :return: Tuple[session id, actor id]
        """
        with self._lock:
            count = self._count
            self._count += 1
        return self._session, count


class LevelDBDimensionManager:
    # tag_ids = {45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 118}

    # A borrowed reference to the leveldb
    _db: LevelDB
    # A class to keep track of unique actor ids
    _actor_counter: Optional[ActorCounter]

    def __init__(self, level: LevelDBFormat):
        """
        :param level: The leveldb format to read data from
        """
        self._db = level.level_db
        self._actor_counter = ActorCounter.from_level(level)
        # self._levels format Dict[level, Dict[Tuple[cx, cz], List[Tuple[full_key, key_extension]]]]
        self._levels: Dict[InternalDimension, Set[ChunkCoordinates]] = {}
        self._dimension_name_map: Dict["Dimension", InternalDimension] = {}
        self._lock = RLock()

        self.register_dimension(None, OVERWORLD)
        self.register_dimension(1, THE_NETHER)
        self.register_dimension(2, THE_END)

        for key in self._db.keys():
            if 9 <= len(key) <= 10 and key[8] in [44, 118]:  # "," "v"
                self._add_chunk(key)

            elif 13 <= len(key) <= 14 and key[12] in [44, 118]:  # "," "v"
                self._add_chunk(key, has_level=True)

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

        with self._lock:
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

    @staticmethod
    def _get_key(cx: int, cz: int, internal_dimension: InternalDimension) -> bytes:
        if internal_dimension is None:
            return struct.pack("<ii", cx, cz)
        else:
            return struct.pack("<iii", cx, cz, internal_dimension)

    def _has_chunk(
        self, cx: int, cz: int, internal_dimension: InternalDimension
    ) -> bool:
        return (
            internal_dimension in self._levels
            and (cx, cz) in self._levels[internal_dimension]
        )

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return self._has_chunk(cx, cz, self._get_internal_dimension(dimension))

    def _add_chunk(self, key_: bytes, has_level: bool = False):
        if has_level:
            cx, cz, level = struct.unpack("<iii", key_[:12])
        else:
            cx, cz = struct.unpack("<ii", key_[:8])
            level = None
        if level not in self._levels:
            self.register_dimension(level)
        self._levels[level].add((cx, cz))

    def get_chunk_data(self, cx: int, cz: int, dimension: "Dimension") -> ChunkData:
        """Get a dictionary of chunk key extension in bytes to the raw data in the key.
        chunk key extension are the character(s) after <cx><cz>[level] in the key
        Will raise ChunkDoesNotExist if the chunk does not exist
        """
        internal_dimension = self._get_internal_dimension(dimension)
        if self._has_chunk(cx, cz, internal_dimension):
            prefix = self._get_key(cx, cz, internal_dimension)
            prefix_len = len(prefix)
            iter_end = prefix + b"\xff\xff\xff\xff"

            chunk_data = ChunkData()
            for key, val in self._db.iterate(prefix, iter_end):
                if key[:prefix_len] == prefix and len(key) <= prefix_len + 2:
                    chunk_data[key[prefix_len:]] = val

            with suppress(KeyError):
                digp_key = b"digp" + prefix
                digp = self._db.get(digp_key)
                chunk_data[
                    b"digp"
                ] = b""  # The presence of this key signals to the put method that this should be created and written
                for i in range(0, (len(digp) // 8) * 8, 8):
                    actor_key = b"actorprefix" + digp[i : i + 8]
                    try:
                        actor_bytes = self._db.get(actor_key)
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
        else:
            raise ChunkDoesNotExist

    def put_chunk_data(
        self,
        cx: int,
        cz: int,
        chunk_data: ChunkData,
        dimension: "Dimension",
    ):
        """pass data to the region file class"""
        # get the region key
        internal_dimension = self._get_internal_dimension(dimension)
        self._levels[internal_dimension].add((cx, cz))
        key_prefix = self._get_key(cx, cz, internal_dimension)

        batch = {}

        if b"digp" in chunk_data:
            # if writing the digp key we need to delete all actors pointed to by the old digp key otherwise there will be memory leaks
            digp_key = b"digp" + key_prefix
            try:
                old_digp = self._db.get(digp_key)
            except KeyError:
                pass
            else:
                for i in range(0, len(old_digp) // 8 * 8, 8):
                    actor_key = b"actorprefix" + old_digp[i : i + 8]
                    self._db.delete(actor_key)

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

                session, uid = self._actor_counter.next()
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

            for actor_ in chunk_data.entity_actor:
                add_actor(actor_, True)

            for actor_ in chunk_data.unknown_actor:
                add_actor(actor_, False)

            del chunk_data[b"digp"]
            batch[digp_key] = b"".join(digp)

        for key, val in chunk_data.items():
            key = key_prefix + key
            if val is None:
                self._db.delete(key)
            else:
                batch[key] = val
        if batch:
            self._db.putBatch(batch)

    def delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        if dimension not in self._dimension_name_map:
            return  # dimension does not exists so chunk cannot

        internal_dimension = self._dimension_name_map[dimension]
        if not self._has_chunk(cx, cz, internal_dimension):
            return  # chunk does not exists

        prefix = self._get_key(cx, cz, internal_dimension)
        prefix_len = len(prefix)
        iter_end = prefix + b"\xff\xff\xff\xff"
        keys = []
        for key, _ in self._db.iterate(prefix, iter_end):
            if key[:prefix_len] == prefix and len(key) <= prefix_len + 2:
                keys.append(key)

        try:
            digp = self._db.get(b"digp" + prefix)
        except KeyError:
            pass
        else:
            self._db.delete(b"digp" + prefix)
            for i in range(0, len(digp) // 8 * 8, 8):
                actor_key = b"actorprefix" + digp[i : i + 8]
                self._db.delete(actor_key)

        self._levels[internal_dimension].remove((cx, cz))
        for key in keys:
            self._db.delete(key)
