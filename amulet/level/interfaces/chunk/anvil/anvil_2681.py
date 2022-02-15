from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

from amulet.api.entity import Entity
from amulet_nbt import TAG_Compound, TAG_List

from .base_anvil_interface import ChunkDataType, ChunkPathType

from .anvil_2529 import (
    Anvil2529Interface,
)


class Anvil2681Interface(Anvil2529Interface):
    """
    Entities moved to a different storage layer
    """

    EntityLayer: ChunkPathType = (
        "entities",
        [("Entities", TAG_List)],
        TAG_List,
    )

    @staticmethod
    def minor_is_valid(key: int):
        return 2681 <= key < 2709

    def _do_decode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ) -> List[Entity]:
        return super()._do_decode_entities(
            chunk, data, floor_cy, height_cy
        ) + self._decode_entity_list(
            self.get_layer_obj(data, self.EntityLayer, pop_last=True)
        )


export = Anvil2681Interface
