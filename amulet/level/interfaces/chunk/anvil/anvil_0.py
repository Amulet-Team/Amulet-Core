from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

from amulet_nbt import TAG_Compound, TAG_Int

from .anvil_na import (
    AnvilNAInterface,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class Anvil0Interface(AnvilNAInterface):
    """
    Added the DataVersion tag
    Note that this has not been tested before 1.12
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 0 <= key < 1444

    def _decode_root(self, chunk: Chunk, root: TAG_Compound):
        self._decode_data_version(root)

    @staticmethod
    def _decode_data_version(compound: TAG_Compound):
        # all versioned data must get removed from data
        if "DataVersion" in compound.value:
            del compound["DataVersion"]

    def _encode_data_version(
        self, root: TAG_Compound, max_world_version: Tuple[str, int]
    ):
        root["DataVersion"] = TAG_Int(max_world_version[1])


export = Anvil0Interface
