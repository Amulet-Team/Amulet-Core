from amulet.level.abc import ChunkHandle as ChunkHandle

from ..abc._chunk_handle import ChunkT as ChunkT
from ._level import JavaLevel as JavaLevel
from ._raw import JavaRawDimension as JavaRawDimension
from .chunk import JavaChunk as JavaChunk

class JavaChunkHandle(ChunkHandle["JavaLevel", "JavaRawDimension", JavaChunk]): ...
