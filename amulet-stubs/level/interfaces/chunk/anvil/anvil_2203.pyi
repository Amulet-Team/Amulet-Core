from .anvil_1934 import Anvil1934Interface as ParentInterface
from .base_anvil_interface import ChunkDataType as ChunkDataType
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk

log: Incomplete

class Anvil2203Interface(ParentInterface):
    """
    Made biomes 3D
    """
    @staticmethod
    def minor_is_valid(key: int): ...
    def _decode_biomes(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _encode_biomes(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
export = Anvil2203Interface
