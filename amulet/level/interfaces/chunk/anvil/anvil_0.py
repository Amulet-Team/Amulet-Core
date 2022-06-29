from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

from amulet_nbt import IntTag

import amulet
from .base_anvil_interface import ChunkPathType, ChunkDataType
from .anvil_na import AnvilNAInterface as ParentInterface

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class Anvil0Interface(ParentInterface):
    """
    Added the DataVersion tag
    Note that this has not been tested before 1.12
    """

    V = None
    RegionDataVersion: ChunkPathType = (
        "region",
        [("DataVersion", IntTag)],
        IntTag,
    )

    def __init__(self):
        super().__init__()
        self._unregister_decoder(self._decode_v_tag)
        self._unregister_encoder(self._encode_v_tag)

        self._register_post_decoder(self._post_decode_data_version)

    @staticmethod
    def minor_is_valid(key: int):
        return 0 <= key < 1444

    def _post_decode_data_version(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        # all versioned data must get removed from data
        self.get_layer_obj(data, self.RegionDataVersion, pop_last=True)

    def _decode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        ents = self._decode_entity_list(
            self.get_layer_obj(data, self.Entities, pop_last=True)
        )
        if amulet.entity_support:
            chunk.entities = ents
        else:
            chunk._native_entities.extend(ents)
            chunk._native_version = (
                "java",
                self.get_layer_obj(data, self.RegionDataVersion).py_int,
            )

    def _init_encode(
        self,
        chunk: Chunk,
        max_world_version: Tuple[str, int],
        floor_cy: int,
        height_cy: int,
    ) -> ChunkDataType:
        data = super()._init_encode(chunk, max_world_version, floor_cy, height_cy)
        self.set_layer_obj(data, self.RegionDataVersion, IntTag(max_world_version[1]))
        return data


export = Anvil0Interface
