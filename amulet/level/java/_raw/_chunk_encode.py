from amulet.level.java.anvil import RawChunkType
from amulet.level.java.chunk import JavaChunk
from ._level import JavaRawLevel
from ._dimension import JavaRawDimension


def native_to_raw(
    raw_level: JavaRawLevel, dimension: JavaRawDimension, chunk: JavaChunk
) -> RawChunkType:
    raise NotImplementedError
