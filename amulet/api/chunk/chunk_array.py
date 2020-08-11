import numpy
from typing import TYPE_CHECKING
import weakref

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class ChunkArray(numpy.ndarray):
    def __new__(cls, parent_chunk: "Chunk", input_array):
        obj = numpy.asarray(input_array).view(cls)
        obj._parent_chunk = weakref.ref(parent_chunk)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._parent_chunk = getattr(obj, "_parent_chunk", None)
