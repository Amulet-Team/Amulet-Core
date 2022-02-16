from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

from amulet.api.entity import Entity
from amulet_nbt import TAG_List, TAG_Int

from .base_anvil_interface import ChunkDataType, ChunkPathType

from .anvil_2529 import (
    Anvil2529Interface,
)


class Anvil2681Interface(Anvil2529Interface):
    """
    Entities moved to a different storage layer
    """

    EntitiesDataVersion: ChunkPathType = (
        "entities",
        [("DataVersion", TAG_Int)],
        TAG_Int,
    )
    EntityLayer: ChunkPathType = (
        "entities",
        [("Entities", TAG_List)],
        TAG_List,
    )

    @staticmethod
    def minor_is_valid(key: int):
        return 2681 <= key < 2709

    def _decode_data_version(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        super()._decode_data_version(chunk, data, floor_cy, height_cy)
        self.get_layer_obj(data, self.EntitiesDataVersion, pop_last=True)

    def _do_decode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ) -> List[Entity]:
        # TODO: it is possible the entity data version does not match the chunk data version
        return super()._do_decode_entities(
            chunk, data, floor_cy, height_cy
        ) + self._decode_entity_list(
            self.get_layer_obj(data, self.EntityLayer, pop_last=True)
        )

    def _init_encode(
        self,
        chunk: Chunk,
        max_world_version: Tuple[str, int],
        floor_cy: int,
        height_cy: int,
    ) -> ChunkDataType:
        data = super()._init_encode(chunk, max_world_version, floor_cy, height_cy)
        self.set_layer_obj(
            data, self.EntitiesDataVersion, TAG_Int(max_world_version[1])
        )
        return data

    # TODO: remove the entity layer if there are no entities


export = Anvil2681Interface
