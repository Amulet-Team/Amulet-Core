from amulet.level.java.anvil import RawChunkType
from amulet.level.java.chunk import JavaChunk
from ._level import JavaRawLevel
from ._dimension import JavaRawDimension


def raw_to_native(
    raw_level: JavaRawLevel,
    dimension: JavaRawDimension,
    raw_chunk: RawChunkType,
) -> JavaChunk:
    raise NotImplementedError
