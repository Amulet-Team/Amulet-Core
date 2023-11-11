import abc
from ._level import BedrockLevelPrivate as BedrockLevelPrivate
from ._raw import BedrockRawDimension as BedrockRawDimension
from .chunk import BedrockChunk as BedrockChunk
from amulet.level.abc import ChunkHandle as ChunkHandle

class BedrockChunkHandle(ChunkHandle[BedrockLevelPrivate, BedrockChunk], metaclass=abc.ABCMeta): ...
