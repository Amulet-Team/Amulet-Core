from __future__ import annotations
from typing import Tuple, Dict, Optional, TYPE_CHECKING

import struct
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberTuple,
)
from .leveldb_28 import (
    LevelDB28Interface as ParentInterface,
)

if TYPE_CHECKING:
    from amulet.api.chunk.blocks import Blocks


class LevelDB29Interface(ParentInterface):

    chunk_version = 29

    def __init__(self):
        super().__init__()
        self._set_feature("data_2d", "height512|biome4096")

    @staticmethod
    def _chunk_key_to_sub_chunk(cy: int, min_y: int) -> int:
        return cy

    @staticmethod
    def _get_sub_chunk_storage_byte(cy: int, min_y: int) -> bytes:
        return struct.pack("b", cy)


export = LevelDB29Interface
