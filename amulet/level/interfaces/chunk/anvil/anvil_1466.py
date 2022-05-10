from __future__ import annotations

import numpy
from typing import Dict
from amulet_nbt import TAG_Compound, TAG_Long_Array
from amulet import log
from amulet.api.chunk import Chunk
from amulet.utils.world_utils import decode_long_array, encode_long_array

from .base_anvil_interface import ChunkPathType, ChunkDataType
from .anvil_1444 import Anvil1444Interface as ParentInterface


class Anvil1466Interface(ParentInterface):
    """
    Added multiple height maps. Now stored in a compound.
    """

    HeightMap = None
    Heightmaps: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("Heightmaps", TAG_Compound)],
        TAG_Compound,
    )

    def __init__(self):
        super().__init__()
        self._set_feature("height_map", "C|V1")

    @staticmethod
    def minor_is_valid(key: int):
        return 1466 <= key < 1467

    def _decode_height(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        heights = self.get_layer_obj(data, self.Heightmaps, pop_last=True)
        chunk.misc["height_mapC"] = h = {}
        for key, value in heights.items():
            if isinstance(value, TAG_Long_Array):
                try:
                    h[key] = decode_long_array(
                        value.value,
                        256,
                        (height_cy << 4).bit_length(),
                        dense=self.LongArrayDense,
                    ).reshape((16, 16)) + (floor_cy << 4)
                except Exception as e:
                    log.warning(e)

    def _encode_height(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        maps = [
            "WORLD_SURFACE_WG",
            "OCEAN_FLOOR_WG",
            "MOTION_BLOCKING",
            "MOTION_BLOCKING_NO_LEAVES",
            "OCEAN_FLOOR",
        ]
        if self._features["height_map"] == "C|V1":  # 1466
            maps = ("LIQUID", "SOLID", "LIGHT", "RAIN")
        elif self._features["height_map"] == "C|V2":  # 1484
            maps.append("LIGHT_BLOCKING")
        elif self._features["height_map"] == "C|V3":  # 1503
            maps.append("LIGHT_BLOCKING")
            maps.append("WORLD_SURFACE")
        elif self._features["height_map"] == "C|V4":  # 1908
            maps.append("WORLD_SURFACE")
        else:
            raise Exception
        heightmaps_temp: Dict[str, numpy.ndarray] = chunk.misc.get("height_mapC", {})
        heightmaps = TAG_Compound()
        for heightmap in maps:
            if (
                heightmap in heightmaps_temp
                and isinstance(heightmaps_temp[heightmap], numpy.ndarray)
                and heightmaps_temp[heightmap].size == 256
            ):
                heightmaps[heightmap] = TAG_Long_Array(
                    encode_long_array(
                        heightmaps_temp[heightmap].ravel() - (floor_cy << 4),
                        (height_cy << 4).bit_length(),
                        self.LongArrayDense,
                    )
                )
        self.set_layer_obj(data, self.Heightmaps, heightmaps)


export = Anvil1466Interface
