from .anvil_1503 import Anvil1503Interface as ParentInterface
from .base_anvil_interface import ChunkDataType as ChunkDataType
from amulet.api.chunk import Chunk as Chunk

class Anvil1519Interface(ParentInterface):
    """
    Sub-chunk sections must have a block array if defined
    """
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
    def _post_encode_sections(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
export = Anvil1519Interface
