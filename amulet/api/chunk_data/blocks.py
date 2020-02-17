from .chunk_array import ChunkArray
import numpy

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class Blocks(ChunkArray):
    def __new__(cls, parent_chunk: "Chunk", input_array=None):
        if input_array is None:
            input_array = numpy.zeros((16, 256, 16), dtype=numpy.int)
        obj = numpy.asarray(input_array).view(cls)
        obj._parent_chunk = parent_chunk
        return obj
