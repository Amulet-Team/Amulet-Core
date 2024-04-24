from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

import amulet
from amulet_nbt import ListTag, IntTag

from .base_anvil_interface import ChunkDataType, ChunkPathType

from .anvil_2529 import Anvil2529Interface as ParentInterface


class Anvil2681Interface(ParentInterface):
    """
    Entities moved to a different storage layer
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 2681 <= key < 2709


export = Anvil2681Interface
