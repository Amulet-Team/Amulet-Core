from ._chunk_handle import BedrockChunkHandle as BedrockChunkHandle
from ._level import BedrockLevelPrivate as BedrockLevelPrivate
from ._raw import BedrockRawDimension as BedrockRawDimension
from amulet.level.abc import Dimension as Dimension

class BedrockDimension(Dimension[BedrockLevelPrivate, BedrockRawDimension, BedrockChunkHandle]):
    def _create_chunk_handle(self, cx: int, cz: int) -> BedrockChunkHandle: ...
