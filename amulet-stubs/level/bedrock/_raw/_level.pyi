from .._level import BedrockLevelPrivate as BedrockLevelPrivate
from ..chunk import BedrockChunk as BedrockChunk
from ._actor_counter import ActorCounter as ActorCounter
from ._chunk import BedrockRawChunk as BedrockRawChunk
from ._constant import DefaultSelection as DefaultSelection, LOCAL_PLAYER as LOCAL_PLAYER, OVERWORLD as OVERWORLD, THE_END as THE_END, THE_NETHER as THE_NETHER
from ._dimension import BedrockRawDimension as BedrockRawDimension
from ._level_dat import BedrockLevelDAT as BedrockLevelDAT
from ._typing import InternalDimension as InternalDimension, PlayerID as PlayerID, RawPlayer as RawPlayer
from _typeshed import Incomplete
from amulet.api.data_types import DimensionID as DimensionID
from amulet.api.errors import PlayerDoesNotExist as PlayerDoesNotExist
from amulet.level.abc import LevelFriend as LevelFriend, RawLevel as RawLevel, RawLevelPlayerComponent as RawLevelPlayerComponent
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from amulet.version import SemanticVersion as SemanticVersion
from leveldb import LevelDB
from threading import RLock
from typing import Callable, Iterable, Optional, Union

log: Incomplete

class BedrockRawLevelPrivate:
    _raw_ref: Callable[[], Optional[BedrockRawLevel]]
    lock: RLock
    closed: bool
    db: Optional[LevelDB]
    dimensions: dict[Union[DimensionID, InternalDimension], BedrockRawDimension]
    dimension_aliases: frozenset[DimensionID]
    actor_counter: Optional[ActorCounter]
    __slots__: Incomplete
    def __init__(self, raw: BedrockRawLevel) -> None: ...
    @property
    def raw(self) -> BedrockRawLevel: ...

class BedrockRawLevel(LevelFriend[BedrockLevelPrivate], RawLevel, RawLevelPlayerComponent[PlayerID, RawPlayer]):
    _r: Optional[BedrockRawLevelPrivate]
    _level_dat: BedrockLevelDAT
    __slots__: Incomplete
    def __init__(self, level_data: BedrockLevelPrivate) -> None: ...
    def _reload(self) -> None: ...
    def _open(self) -> None: ...
    def _close(self) -> None: ...
    @property
    def level_db(self) -> LevelDB:
        """
        The leveldb database.
        Changes made to this are made directly to the level.
        """
    @property
    def level_dat(self) -> BedrockLevelDAT:
        """Get the level.dat file for the world"""
    @level_dat.setter
    def level_dat(self, level_dat: BedrockLevelDAT): ...
    @property
    def max_game_version(self) -> SemanticVersion:
        """
        The game version that the level was last opened in.
        This is used to determine the data format to save in.
        """
    @property
    def last_played(self) -> int: ...
    def _find_dimensions(self) -> None: ...
    def dimensions(self) -> frozenset[DimensionID]: ...
    def get_dimension(self, dimension: Union[DimensionID, InternalDimension]) -> BedrockRawDimension: ...
    def players(self) -> Iterable[PlayerID]: ...
    def has_player(self, player_id: PlayerID) -> bool: ...
    def get_raw_player(self, player_id: PlayerID) -> RawPlayer: ...
    def set_raw_player(self, player_id: PlayerID, player: RawPlayer): ...
