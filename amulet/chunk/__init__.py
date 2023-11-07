from __future__ import annotations
from typing import TypeVar


class Chunk:
    pass


ChunkT = TypeVar("ChunkT", bound=Chunk)
RawChunkT = TypeVar("RawChunkT")
