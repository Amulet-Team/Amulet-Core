from __future__ import annotations

from typing import TYPE_CHECKING, Callable
import struct
from contextlib import suppress
import logging
from collections.abc import Iterator

from amulet_nbt import (
    NamedTag,
    LongTag,
    StringTag,
    CompoundTag,
    NBTLoadError,
    read_nbt,
    utf8_escape_encoding,
)

from amulet.data_types import DimensionId, ChunkCoordinates
from amulet.block import Block, BlockStack
from amulet.biome import Biome
from amulet.selection import SelectionGroup
from amulet.errors import ChunkDoesNotExist
from amulet.version import VersionNumber
from amulet.level.abc import RawDimension, RawLevelFriend
from ._chunk import BedrockRawChunk
from ._chunk_decode import raw_to_native
from ._chunk_encode import native_to_raw
from ._constant import THE_NETHER, THE_END
from ._typing import InternalDimension
from ..chunk import BedrockChunk

if TYPE_CHECKING:
    from ._level import BedrockRawLevel

log = logging.getLogger(__name__)


class BedrockRawDimension(
    RawLevelFriend["BedrockRawLevel"], RawDimension[BedrockRawChunk, BedrockChunk]
):
    def __init__(
        self,
        raw_level_ref: Callable[[], BedrockRawLevel | None],
        internal_dimension: InternalDimension,
        alias: DimensionId,
        bounds: SelectionGroup,
    ) -> None:
        super().__init__(raw_level_ref)
        self._internal_dimension = internal_dimension
        self._alias = alias
        self._bounds = bounds

    @property
    def dimension_id(self) -> DimensionId:
        return self._alias

    @property
    def internal_dimension_id(self) -> InternalDimension:
        return self._internal_dimension

    def bounds(self) -> SelectionGroup:
        """The editable region of the dimension."""
        return self._bounds

    def default_block(self) -> BlockStack:
        """The default block for this dimension"""
        return BlockStack(
            Block("bedrock", VersionNumber(1, 20, 61), "minecraft", "air")
        )

    def default_biome(self) -> Biome:
        """The default biome for this dimension"""
        # todo: is this stored in the data somewhere?
        if self.dimension_id == THE_NETHER:
            return Biome("bedrock", VersionNumber(1, 20, 61), "minecraft", "hell")
        elif self.dimension_id == THE_END:
            return Biome("bedrock", VersionNumber(1, 20, 61), "minecraft", "the_end")
        else:
            return Biome("bedrock", VersionNumber(1, 20, 61), "minecraft", "plains")

    def all_chunk_coords(self) -> Iterator[ChunkCoordinates]:
        if self._internal_dimension is None:
            mask = slice(8, 9)
            key_len = 9
            keys = (b",", b"v")
        else:
            mask = slice(8, 13)
            key_len = 13
            dim = struct.pack("<i", self._internal_dimension)
            keys = (dim + b",", dim + b"v")
        for key in self._r.level_db.keys():
            if len(key) == key_len and key[mask] in keys:
                yield struct.unpack("<ii", key[:8])

    def _chunk_prefix(self, cx: int, cz: int) -> bytes:
        if self._internal_dimension is None:
            return struct.pack("<ii", cx, cz)
        else:
            return struct.pack("<iii", cx, cz, self._internal_dimension)

    def has_chunk(self, cx: int, cz: int) -> bool:
        key = self._chunk_prefix(cx, cz)
        return any(key + tag in self._r.level_db for tag in (b",", b"v"))

    def delete_chunk(self, cx: int, cz: int) -> None:
        if not self.has_chunk(cx, cz):
            return  # chunk does not exists

        db = self._r.level_db
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
        """Get the raw data for the chunk.

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

        chunk_data = BedrockRawChunk()
        for key, val in self._r.level_db.iterate(prefix, iter_end):
            if key[:prefix_len] == prefix and len(key) <= prefix_len + 2:
                chunk_data.chunk_data[key[prefix_len:]] = val

        with suppress(KeyError):
            digp_key = b"digp" + prefix
            digp = self._r.level_db.get(digp_key)
            chunk_data.chunk_data[b"digp"] = (
                b""  # The presence of this key signals to the put method that this should be created and written
            )
            for i in range(0, (len(digp) // 8) * 8, 8):
                actor_key = b"actorprefix" + digp[i : i + 8]
                try:
                    actor_bytes = self._r.level_db.get(actor_key)
                    actor = read_nbt(
                        actor_bytes,
                        little_endian=True,
                        string_encoding=utf8_escape_encoding,
                    )
                    actor_tag = actor.compound
                except KeyError:
                    log.error(f"Could not find actor {actor_key!r}. Skipping.")
                except NBTLoadError:
                    log.error(f"Failed to parse actor {actor_key!r}. Skipping.")
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
                                f"Actor {actor_key!r} has an unknown format. Please report this to a developer {repr(internal_components)}"
                            )
                            for k, v in internal_components.items():
                                if isinstance(v, CompoundTag) and isinstance(
                                    v.get("StorageKey"), StringTag
                                ):
                                    v["StorageKey"] = StringTag()
                            chunk_data.unknown_actor.append(actor)
                    else:
                        log.error(
                            f"internalComponents was not valid for actor {actor_key!r}. Skipping."
                        )
                        continue

        return chunk_data

    def set_raw_chunk(self, cx: int, cz: int, chunk: BedrockRawChunk) -> None:
        """
        Set the raw data for a chunk
        :param cx: The chunk x coordinate
        :param cz: The chunk z coordinate
        :param chunk: The chunk data to set.
        :return:
        """
        key_prefix = self._chunk_prefix(cx, cz)

        batch = {}

        if b"digp" in chunk.chunk_data:
            # if writing the digp key we need to delete all actors pointed to by the old digp key otherwise there will be memory leaks
            digp_key = b"digp" + key_prefix
            try:
                old_digp = self._r.level_db.get(digp_key)
            except KeyError:
                pass
            else:
                for i in range(0, len(old_digp) // 8 * 8, 8):
                    actor_key = b"actorprefix" + old_digp[i : i + 8]
                    self._r.level_db.delete(actor_key)

            digp = []

            def add_actor(actor: NamedTag, is_entity: bool) -> None:
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

                session, uid = self._r._o.actor_counter.next()
                # session is already negative
                key = struct.pack(">ii", -session, uid)
                # b'\x00\x00\x00\x01\x00\x00\x00\x0c' 1, 12
                for storage in storages:
                    storage["StorageKey"] = StringTag(utf8_escape_encoding.decode(key))
                # -4294967284 ">q" b'\xff\xff\xff\xff\x00\x00\x00\x0c' ">ii" -1, 12
                actor_tag["UniqueID"] = LongTag(
                    struct.unpack(">q", struct.pack(">ii", session, uid))[0]
                )

                batch[b"actorprefix" + key] = actor.save_to(
                    little_endian=True,
                    compressed=False,
                    string_encoding=utf8_escape_encoding,
                )
                digp.append(key)

            for actor_ in chunk.entity_actor:
                add_actor(actor_, True)

            for actor_ in chunk.unknown_actor:
                add_actor(actor_, False)

            del chunk.chunk_data[b"digp"]
            batch[digp_key] = b"".join(digp)

        # TODO: find all existing keys for this chunk in the database and delete them
        for key, val in chunk.chunk_data.items():
            key = key_prefix + key
            if val is None:
                self._r.level_db.delete(key)
            else:
                batch[key] = val
        if batch:
            self._r.level_db.putBatch(batch)

    def raw_chunk_to_native_chunk(
        self, raw_chunk: BedrockRawChunk, cx: int, cz: int
    ) -> BedrockChunk:
        return raw_to_native(self._r, self, raw_chunk)

    def native_chunk_to_raw_chunk(
        self, chunk: BedrockChunk, cx: int, cz: int
    ) -> BedrockRawChunk:
        return native_to_raw(self._r, self, chunk)
