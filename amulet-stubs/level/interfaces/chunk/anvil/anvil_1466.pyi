from .anvil_1444 import Anvil1444Interface as ParentInterface
from .base_anvil_interface import ChunkDataType as ChunkDataType, ChunkPathType as ChunkPathType
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.utils.world_utils import decode_long_array as decode_long_array, encode_long_array as encode_long_array

log: Incomplete

class Anvil1466Interface(ParentInterface):
    """
    Added multiple height maps. Now stored in a compound.
    """
    HeightMap: Incomplete
    Heightmaps: ChunkPathType
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
    def _decode_height(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _encode_height(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
export = Anvil1466Interface
