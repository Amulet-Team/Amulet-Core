from __future__ import annotations

import numpy
from amulet_nbt import TAG_Int_Array
from amulet import log
from amulet.api.chunk import Chunk
from .base_anvil_interface import ChunkDataType
from .anvil_1934 import Anvil1934Interface as ParentInterface


class Anvil2203Interface(ParentInterface):
    """
    Made biomes 3D
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529

    def _decode_biomes(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        biomes = self.get_layer_obj(data, self.Biomes, pop_last=True)
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
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        if chunk.status.value > -0.7:
            chunk.biomes.convert_to_3d()
            self.set_layer_obj(
                data,
                self.Biomes,
                TAG_Int_Array(
                    numpy.transpose(
                        numpy.asarray(
                            chunk.biomes[
                                :, floor_cy * 4 : (floor_cy + height_cy) * 4, :
                            ]
                        ).astype(numpy.uint32),
                        (1, 2, 0),
                    ).ravel()  # YZX -> XYZ
                ),
            )


export = Anvil2203Interface
