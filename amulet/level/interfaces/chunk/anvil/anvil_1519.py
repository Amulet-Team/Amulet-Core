from __future__ import annotations

from amulet.api.chunk import Chunk

from .base_anvil_interface import ChunkDataType
from .anvil_1503 import Anvil1503Interface as ParentInterface


class Anvil1519Interface(ParentInterface):
    """
    Sub-chunk sections must have a block array if defined
    """

    def __init__(self):
        super().__init__()
        self._register_post_encoder(self._post_encode_sections)

    @staticmethod
    def minor_is_valid(key: int):
        return 1519 <= key < 1901

    def _post_encode_sections(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        sections = self.get_layer_obj(data, self.Sections)
        for section_index in range(len(sections) - 1, -1, -1):
            if (
                "BlockStates" not in sections[section_index]
                or "Palette" not in sections[section_index]
            ):
                del sections[section_index]


export = Anvil1519Interface
