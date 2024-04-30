from __future__ import annotations

import numpy
from amulet_nbt import IntArrayTag, CompoundTag
from amulet.api.chunk import Chunk
from .base_anvil_interface import ChunkPathType, ChunkDataType
from .anvil_1466 import Anvil1466Interface as ParentInterface


class Anvil1467Interface(ParentInterface):
    """
    Biomes now stored in an int array
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 1467 <= key < 1484


export = Anvil1467Interface
