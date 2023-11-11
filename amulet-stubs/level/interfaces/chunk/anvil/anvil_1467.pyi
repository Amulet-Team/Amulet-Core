from .anvil_1466 import Anvil1466Interface as ParentInterface
from .base_anvil_interface import ChunkDataType as ChunkDataType, ChunkPathType as ChunkPathType
from amulet.api.chunk import Chunk as Chunk

class Anvil1467Interface(ParentInterface):
    """
    Biomes now stored in an int array
    """
    Biomes: ChunkPathType
    @staticmethod
    def minor_is_valid(key: int): ...
    def _encode_biomes(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
export = Anvil1467Interface
