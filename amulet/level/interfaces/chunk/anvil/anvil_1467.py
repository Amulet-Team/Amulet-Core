from __future__ import annotations

import numpy
from amulet_nbt import TAG_Int_Array, TAG_Compound
from amulet.api.chunk import Chunk
from .base_anvil_interface import ChunkPathType, ChunkDataType
from .anvil_1466 import Anvil1466Interface as ParentInterface


class Anvil1467Interface(ParentInterface):
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

    def _encode_biomes(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        if chunk.status.value > -0.7:
            chunk.biomes.convert_to_2d()
            self.set_layer_obj(
                data,
                self.Biomes,
                TAG_Int_Array(chunk.biomes.astype(dtype=numpy.uint32).ravel()),
            )


export = Anvil1467Interface
