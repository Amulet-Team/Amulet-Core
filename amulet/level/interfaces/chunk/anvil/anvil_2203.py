from __future__ import annotations

from typing import Tuple
import numpy
from amulet_nbt import TAG_Compound, TAG_Int_Array
from amulet import log
from amulet.api.chunk import Chunk
from .anvil_1934 import (
    Anvil1934Interface,
)
from .feature_enum import BiomeState


class Anvil2203Interface(Anvil1934Interface):
    def __init__(self):
        super().__init__()
        self._set_feature("biomes", BiomeState.IA1024)  # optional

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529

    def _decode_biomes(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int] = (0, 256)
    ):
        biomes = compound.pop("Biomes")
        min_y = bounds[0]
        height = bounds[1] - min_y
        arr_start = min_y // 16
        arr_height = height // 4
        if isinstance(biomes, TAG_Int_Array):
            if biomes.value.size == 16 * arr_height:
                chunk.biomes = {
                    sy + arr_start: arr
                    for sy, arr in enumerate(
                        numpy.split(
                            numpy.transpose(
                                biomes.astype(numpy.uint32).reshape(arr_height, 4, 4),
                                (2, 0, 1),
                            ),  # YZX -> XYZ
                            arr_height // 4,
                            1,
                        )
                    )
                }
            else:
                log.error(
                    f"Expected a biome array of size {arr_height * 4 * 4} but got an array of size {biomes.value.size}"
                )
        else:
            log.error(
                f"Expected a TAG_Int_Array biome array but got {biomes.__class__.__name__}"
            )


export = Anvil2203Interface
