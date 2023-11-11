from .anvil_2529 import Anvil2529Interface as ParentInterface
from .base_anvil_interface import ChunkDataType as ChunkDataType, ChunkPathType as ChunkPathType
from amulet.api.chunk import Chunk as Chunk

class Anvil2681Interface(ParentInterface):
    """
    Entities moved to a different storage layer
    """
    EntitiesDataVersion: ChunkPathType
    EntityLayer: ChunkPathType
    @staticmethod
    def minor_is_valid(key: int): ...
    def _post_decode_data_version(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _decode_entities(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _encode_entities(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
export = Anvil2681Interface
