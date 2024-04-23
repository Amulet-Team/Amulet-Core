from __future__ import annotations

from typing import Dict
import logging

import numpy

from amulet_nbt import CompoundTag, LongArrayTag
from amulet.api.chunk import Chunk
from amulet.utils.world_utils import decode_long_array, encode_long_array

from .base_anvil_interface import ChunkPathType, ChunkDataType
from .anvil_1444 import Anvil1444Interface as ParentInterface

log = logging.getLogger(__name__)


class Anvil1466Interface(ParentInterface):
    """
    Added multiple height maps. Now stored in a compound.
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 1466 <= key < 1467


export = Anvil1466Interface
