from __future__ import annotations

from typing import Tuple
from amulet_nbt import TAG_Compound, TAG_Long_Array
from amulet import log
from amulet.api.chunk import Chunk
from amulet.utils.world_utils import decode_long_array, encode_long_array

from .anvil_1444 import (
    Anvil1444Interface,
)


class Anvil1466Interface(Anvil1444Interface):
    def __init__(self):
        super().__init__()
        self._set_feature("height_map", "C|V1")

    @staticmethod
    def minor_is_valid(key: int):
        return 1466 <= key < 1467

    def _decode_height(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int] = (0, 256)
    ):
        heights = self.get_obj(compound, "Heightmaps", TAG_Compound)
        chunk.misc["height_mapC"] = h = {}
        for key, value in heights.items():
            if isinstance(value, TAG_Long_Array):
                try:
                    h[key] = (
                        decode_long_array(
                            value.value,
                            256,
                            (bounds[1] - bounds[0]).bit_length(),
                            dense=self._features["long_array_format"] == "compact",
                        ).reshape((16, 16))
                        + bounds[0]
                    )
                except Exception as e:
                    log.warning(e)


export = Anvil1466Interface
