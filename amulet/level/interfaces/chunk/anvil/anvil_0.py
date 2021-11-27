from __future__ import annotations

from typing import TYPE_CHECKING

from amulet_nbt import TAG_Compound

from .anvil_na import (
    AnvilNAInterface,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class Anvil112Interface(AnvilNAInterface):
    """Added the DataVersion tag"""

    @staticmethod
    def minor_is_valid(key: int):
        return 0 <= key < 1444

    def _decode_root(self, chunk: Chunk, root: TAG_Compound):
        self._remove_data_version(root)

    @staticmethod
    def _remove_data_version(compound: TAG_Compound):
        # all versioned data must get removed from data
        if "DataVersion" in compound.value:
            del compound["DataVersion"]


export = Anvil112Interface
