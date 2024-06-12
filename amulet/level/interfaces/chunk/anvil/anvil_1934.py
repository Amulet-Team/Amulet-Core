from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

from amulet_nbt import CompoundTag, ByteTag

from .base_anvil_interface import ChunkDataType, ChunkPathType

from .anvil_1912 import Anvil1912Interface as ParentInterface


class Anvil1934Interface(ParentInterface):
    """
    Made lighting optional
    """

    isLightOn: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("isLightOn", ByteTag)],
        ByteTag,
    )

    def __init__(self):
        super().__init__()
        self._set_feature("light_optional", "true")
        self._register_encoder(self._encode_is_light_on)
        self._register_decoder(self._decode_is_light_on)

    @staticmethod
    def minor_is_valid(key: int):
        return 1934 <= key < 2203

    def _decode_is_light_on(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["isLightOn"] = self.get_layer_obj(
            data, self.isLightOn, pop_last=True
        )

    def _encode_is_light_on(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        is_light_on = bool(chunk.misc.pop("isLightOn", None))
        self.set_layer_obj(data, self.isLightOn, ByteTag(is_light_on))


export = Anvil1934Interface
