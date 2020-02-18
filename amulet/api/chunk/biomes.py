from .chunk_array import ChunkArray
import numpy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class Biomes(ChunkArray):
    def __new__(cls, parent_chunk: "Chunk", input_array):
        obj = numpy.asarray(input_array, dtype=numpy.uint32).view(cls)
        obj._parent_chunk = parent_chunk
        if obj.size == 256:
            obj.resize(16, 16)
        elif obj.size == 1024:
            obj.resize(8, 8, 16)  # TODO: honestly don't know what the format of this is
        return obj

    def convert_to_format(self, length):
        if length in [256, 1024]:
            # TODO: proper conversion
            if length > self.size:
                self._parent_chunk.biomes = numpy.concatenate(
                    (self.ravel(), numpy.zeros(length - self.size, dtype=self.dtype))
                )
            elif length < self.size:
                self._parent_chunk.biomes = self.ravel()[:length]
            return self._parent_chunk.biomes
        else:
            raise Exception(f"Format length {length} is invalid")
