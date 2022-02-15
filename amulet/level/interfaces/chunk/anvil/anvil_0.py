from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

from amulet_nbt import TAG_Compound, TAG_Int

from .base_anvil_interface import ChunkPathType, ChunkDataType
from .anvil_na import AnvilNAInterface

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class Anvil0Interface(AnvilNAInterface):
    """
    Added the DataVersion tag
    Note that this has not been tested before 1.12
    """

    V = None
    DataVersion: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("DataVersion", TAG_Int)],
        TAG_Int,
    )

    def __init__(self):
        super().__init__()
        self._register_decoder(self._decode_data_version)

    @staticmethod
    def minor_is_valid(key: int):
        return 0 <= key < 1444

    def _decode_data_version(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        # all versioned data must get removed from data
        self.get_layer_obj(data, self.DataVersion, pop_last=True)

    # def _encode_data_version(
    #     self, root: TAG_Compound, max_world_version: Tuple[str, int]
    # ):
    #     root["DataVersion"] = TAG_Int(max_world_version[1])


export = Anvil0Interface
