import abc
from .dimension import ChunkData as ChunkData
from .interface.chunk import BaseLevelDBInterface as BaseLevelDBInterface, get_interface as get_interface
from .interface.chunk.leveldb_chunk_versions import game_to_chunk_version as game_to_chunk_version
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, Dimension as Dimension, VersionNumberTuple as VersionNumberTuple
from amulet.api.wrapper import WorldFormatWrapper as WorldFormatWrapper
from amulet.player import Player as Player
from typing import Any, Optional, Tuple

OVERWORLD: str
THE_NETHER: str
THE_END: str

class LevelDBFormat(WorldFormatWrapper[VersionNumberTuple], metaclass=abc.ABCMeta):
    """
    This FormatWrapper class exists to interface with the Bedrock world format.
    """
    def _get_interface(self, raw_chunk_data: Optional[Any] = ...) -> BaseLevelDBInterface: ...
    def _get_interface_key(self, raw_chunk_data: Optional[ChunkData] = ...) -> int: ...
    def _decode(self, interface: BaseLevelDBInterface, dimension: Dimension, cx: int, cz: int, raw_chunk_data: Any) -> Tuple[Chunk, AnyNDArray]: ...
    def _encode(self, interface: BaseLevelDBInterface, chunk: Chunk, dimension: Dimension, chunk_palette: AnyNDArray) -> Any: ...
    def _load_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
