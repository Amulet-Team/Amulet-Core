from __future__ import annotations

import amulet.level.abc._dimension
import amulet.level.java._chunk_handle
from amulet.level.abc._dimension import Dimension
from amulet.level.java._chunk_handle import JavaChunkHandle

__all__ = ["Dimension", "JavaChunkHandle", "JavaDimension"]

class JavaDimension(amulet.level.abc._dimension.Dimension):
    def _create_chunk_handle(
        self, cx: int, cz: int
    ) -> amulet.level.java._chunk_handle.JavaChunkHandle: ...
