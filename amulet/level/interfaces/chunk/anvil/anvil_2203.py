from __future__ import annotations

from typing import Tuple
import numpy
from amulet_nbt import TAG_Compound, TAG_Int_Array
from amulet import log
from amulet.api.chunk import Chunk
from .anvil_1934 import (
    Anvil1934Interface,
)


class Anvil2203Interface(Anvil1934Interface):
    """
    Made biomes 3D
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529

    def _decode_biomes(self, chunk: Chunk, compound: TAG_Compound, floor_cy: int):
        biomes = compound.pop("Biomes", None)
        if isinstance(biomes, TAG_Int_Array):
            if (len(biomes) / 16) % 4:
                log.error(
                    f"The biome array size must be 4x4x4xN but got an array of size {biomes.value.size}"
                )
            else:
                arr = numpy.transpose(
                    biomes.astype(numpy.uint32).reshape((-1, 4, 4)),
                    (2, 0, 1),
                )  # YZX -> XYZ
                chunk.biomes = {
                    sy + floor_cy: arr
                    for sy, arr in enumerate(
                        numpy.split(
                            arr,
                            arr.shape[1] // 4,
                            1,
                        )
                    )
                }

    def _encode_biomes(
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    ):
        if chunk.status.value > -0.7:
            chunk.biomes.convert_to_3d()
            min_y, max_y = bounds
            level["Biomes"] = TAG_Int_Array(
                numpy.transpose(
                    numpy.asarray(chunk.biomes[:, min_y // 4 : max_y // 4, :]).astype(
                        numpy.uint32
                    ),
                    (1, 2, 0),
                ).ravel()  # YZX -> XYZ
            )


export = Anvil2203Interface
