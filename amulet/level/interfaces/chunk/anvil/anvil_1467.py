from __future__ import annotations

from typing import Tuple
import numpy
from amulet_nbt import TAG_Int_Array, TAG_Compound
from amulet.api.chunk import Chunk
from .anvil_1466 import (
    Anvil1466Interface,
)


class Anvil1467Interface(Anvil1466Interface):
    """
    Biomes now stored in an int array
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 1467 <= key < 1484

    def _decode_biomes(self, chunk: Chunk, compound: TAG_Compound, floor_cy: int):
        biomes = compound.pop("Biomes", None)
        if isinstance(biomes, TAG_Int_Array) and biomes.value.size == 256:
            chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))

    def _encode_biomes(
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    ):
        if chunk.status.value > -0.7:
            chunk.biomes.convert_to_2d()
            level["Biomes"] = TAG_Int_Array(
                chunk.biomes.astype(dtype=numpy.uint32).ravel()
            )


export = Anvil1467Interface
