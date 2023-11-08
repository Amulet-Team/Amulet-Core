from __future__ import annotations

from typing import Iterable, TYPE_CHECKING
import struct
from contextlib import suppress
import logging

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

from amulet.api.data_types import (
    DimensionID,
    ChunkCoordinates,
    BiomeType,
)
from amulet.block import Block
from amulet.selection import SelectionGroup
from amulet.api.errors import ChunkDoesNotExist
from amulet.level.abc import RawDimension
from ._chunk import BedrockRawChunk
from ._level_friend import BedrockRawLevelFriend
from ._constant import OVERWORLD, THE_NETHER, THE_END
from ._typing import InternalDimension

if TYPE_CHECKING:
    from ._level import BedrockRawLevelPrivate

log = logging.getLogger(__name__)


class BedrockRawDimension(BedrockRawLevelFriend, AbstractRawDimension):
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
        return Block(self._r.raw.max_game_version, "minecraft", "air")

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

    def get_raw_chunk(self, cx: int, cz: int) -> BedrockRawChunk:
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

        chunk_data = BedrockRawChunk()
        for key, val in self._r.db.iterate(prefix, iter_end):
            if key[:prefix_len] == prefix and len(key) <= prefix_len + 2:
                chunk_data.chunk_data[key[prefix_len:]] = val

        with suppress(KeyError):
            digp_key = b"digp" + prefix
            digp = self._r.db.get(digp_key)
            chunk_data.chunk_data[
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

    def set_raw_chunk(self, cx: int, cz: int, chunk: BedrockRawChunk):
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

            del chunk.chunk_data[b"digp"]
            batch[digp_key] = b"".join(digp)

        for key, val in chunk.chunk_data.items():
            key = key_prefix + key
            if val is None:
                self._r.db.delete(key)
            else:
                batch[key] = val
        if batch:
            self._r.db.putBatch(batch)
