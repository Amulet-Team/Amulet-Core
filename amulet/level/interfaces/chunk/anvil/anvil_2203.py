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

    def _decode_biomes(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int]
    ):
        biomes = compound.pop("Biomes", None)
        if isinstance(biomes, TAG_Int_Array):
            min_y = bounds[0]
            height = bounds[1] - min_y
            arr_start = min_y // 16
            arr_height = height // 4
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
