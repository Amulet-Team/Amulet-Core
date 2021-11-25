from __future__ import annotations

import numpy
from amulet_nbt import TAG_Int_Array, TAG_Compound
from amulet.api.chunk import Chunk
from .anvil_1466 import (
    Anvil1466Interface,
)
from .feature_enum import BiomeState


class Anvil1467Interface(Anvil1466Interface):
    def __init__(self):
        super().__init__()
        self._set_feature("biomes", BiomeState.IA256)

    @staticmethod
    def minor_is_valid(key: int):
        return 1467 <= key < 1484

    def _decode_biomes(self, chunk: Chunk, compound: TAG_Compound):
        biomes = compound.pop("Biomes")
        if isinstance(biomes, TAG_Int_Array) and biomes.value.size == 256:
            chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))


export = Anvil1467Interface
