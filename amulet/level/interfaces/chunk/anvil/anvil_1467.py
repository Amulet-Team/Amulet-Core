from __future__ import annotations

from typing import Tuple
import numpy
from amulet_nbt import TAG_Int_Array, TAG_Compound
from amulet.api.chunk import Chunk
from .base_anvil_interface import ChunkPathType, ChunkDataType
from .anvil_1466 import (
    Anvil1466Interface,
)


class Anvil1467Interface(Anvil1466Interface):
    """
    Biomes now stored in an int array
    """

    Biomes: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("Biomes", TAG_Int_Array)],
        None,
    )

    @staticmethod
    def minor_is_valid(key: int):
        return 1467 <= key < 1484

    # def _encode_biomes(
    #     self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    # ):
    #     if chunk.status.value > -0.7:
    #         chunk.biomes.convert_to_2d()
    #         level["Biomes"] = TAG_Int_Array(
    #             chunk.biomes.astype(dtype=numpy.uint32).ravel()
    #         )


export = Anvil1467Interface
