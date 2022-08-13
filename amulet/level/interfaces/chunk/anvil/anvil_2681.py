from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

import amulet
from amulet.api.entity import Entity
from amulet_nbt import ListTag, IntTag

from .base_anvil_interface import ChunkDataType, ChunkPathType

from .anvil_2529 import Anvil2529Interface as ParentInterface


class Anvil2681Interface(ParentInterface):
    """
    Entities moved to a different storage layer
    """

    EntitiesDataVersion: ChunkPathType = (
        "entities",
        [("DataVersion", IntTag)],
        IntTag,
    )
    EntityLayer: ChunkPathType = (
        "entities",
        [("Entities", ListTag)],
        ListTag,
    )

    @staticmethod
    def minor_is_valid(key: int):
        return 2681 <= key < 2709

    def _post_decode_data_version(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        super()._post_decode_data_version(chunk, data, floor_cy, height_cy)
        self.get_layer_obj(data, self.EntitiesDataVersion, pop_last=True)

    def _decode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        # TODO: it is possible the entity data version does not match the chunk data version
        ents = self._decode_entity_list(
            self.get_layer_obj(data, self.Entities, pop_last=True)
        ) + self._decode_entity_list(
            self.get_layer_obj(data, self.EntityLayer, pop_last=True)
        )
        if amulet.entity_support:
            chunk.entities = ents
        else:
            chunk._native_entities.extend(ents)
            chunk._native_version = (
                "java",
                self.get_layer_obj(data, self.EntitiesDataVersion),
            )

    def _encode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        try:
            platform, version = chunk._native_version
        except:
            pass
        else:
            if platform == "java" and isinstance(version, int):
                super()._encode_entities(chunk, data, floor_cy, height_cy)
                self.set_layer_obj(data, self.EntitiesDataVersion, IntTag(version))
                return
        data.pop(self.EntitiesDataVersion[0], None)


export = Anvil2681Interface
