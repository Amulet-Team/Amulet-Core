from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

from amulet_nbt import CompoundTag, ByteTag

from .base_anvil_interface import ChunkDataType, ChunkPathType

from .anvil_1912 import Anvil1912Interface as ParentInterface


class Anvil1934Interface(ParentInterface):
    isLightOn: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("isLightOn", ByteTag)],
        ByteTag,
    )
    """
    Made lighting optional
    Made game recalculate lighting 
    """

    class Anvil1934Interface(ParentInterface):
        isLightOn: ChunkPathType = (
            "region",
            [("Level", CompoundTag), ("isLightOn", ByteTag)],
            ByteTag,
        )
        """
        Made game recalulate lighting 
        """

        def __init__(self):
            super().__init__()
            self._set_feature("light_optional", "true")

            self._register_decoder(self._decode_islighton)
            self._register_encoder(self._encode_islighton)

        @staticmethod
        def minor_is_valid(key: int):
            return 1934 <= key < 2203

        def _decode_islighton(
            self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
        ):
            light_on = self.get_layer_obj(data, self.isLightOn)
            if light_on == ByteTag(1):
                chunk.set_light_off = True

        def _encode_islighton(
            self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
        ):
            if chunk.set_light_off:
                self.set_layer_obj(data, self.isLightOn, ByteTag(0))

    export = Anvil1934Interface
