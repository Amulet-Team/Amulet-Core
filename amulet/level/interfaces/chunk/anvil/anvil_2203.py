from __future__ import annotations

import logging

import numpy
from amulet_nbt import IntArrayTag
from amulet.api.chunk import Chunk
from .base_anvil_interface import ChunkDataType
from .anvil_1934 import Anvil1934Interface as ParentInterface

log = logging.getLogger(__name__)


class Anvil2203Interface(ParentInterface):
    """
    Made biomes 3D
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529


export = Anvil2203Interface
