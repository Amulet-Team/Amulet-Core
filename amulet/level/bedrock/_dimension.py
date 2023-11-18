from typing import TYPE_CHECKING

from amulet.level.abc import Dimension
from ._chunk_handle import BedrockChunkHandle

if TYPE_CHECKING:
    from ._level import BedrockLevel
    from ._raw import BedrockRawDimension


class BedrockDimension(
    Dimension["BedrockLevel", "BedrockRawDimension", BedrockChunkHandle]
):
    def _create_chunk_handle(self, cx: int, cz: int) -> BedrockChunkHandle:
        return BedrockChunkHandle(self._l, self._chunk_history, self.dimension, cx, cz)
