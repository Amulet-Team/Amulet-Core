from .anvil_na import AnvilNAInterface as ParentInterface
from .base_anvil_interface import ChunkDataType as ChunkDataType, ChunkPathType as ChunkPathType
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from typing import Tuple

class Anvil0Interface(ParentInterface):
    """
    Added the DataVersion tag
    Note that this has not been tested before 1.12
    """
    V: Incomplete
    RegionDataVersion: ChunkPathType
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
    def _post_decode_data_version(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _decode_entities(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _init_encode(self, chunk: Chunk, max_world_version: Tuple[str, int], floor_cy: int, height_cy: int) -> ChunkDataType: ...
export = Anvil0Interface
