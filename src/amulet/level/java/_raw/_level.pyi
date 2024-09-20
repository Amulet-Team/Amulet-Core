from dataclasses import dataclass
from threading import RLock
from typing import BinaryIO, Callable

from _typeshed import Incomplete
from amulet.biome import Biome as Biome
from amulet.block import Block as Block
from amulet.block import BlockStack as BlockStack
from amulet.data_types import DimensionId as DimensionId
from amulet.errors import LevelWriteError as LevelWriteError
from amulet.game import get_game_version as get_game_version
from amulet.level.abc import IdRegistry as IdRegistry
from amulet.level.abc import RawLevel as RawLevel
from amulet.level.java.anvil import AnvilDimension as AnvilDimension
from amulet.selection import SelectionBox as SelectionBox
from amulet.selection import SelectionGroup as SelectionGroup
from amulet.utils.signal import Signal as Signal
from amulet.utils.signal import SignalInstanceCacheName as SignalInstanceCacheName
from amulet.utils.weakref import DetachableWeakRef as DetachableWeakRef
from amulet.version import VersionNumber as VersionNumber
from amulet_nbt import NamedTag

from ._constant import OVERWORLD as OVERWORLD
from ._constant import THE_END as THE_END
from ._constant import THE_NETHER as THE_NETHER
from ._constant import DefaultSelection as DefaultSelection
from ._data_pack import DataPack as DataPack
from ._data_pack import DataPackManager as DataPackManager
from ._dimension import JavaRawDimension as JavaRawDimension
from ._typing import InternalDimensionId as InternalDimensionId

log: Incomplete

@dataclass
class JavaCreateArgsV1:
    """A class to house call arguments to create.

    If the call arguments to create need to be modified in the future a new arguments class can be created.
    The create method can inspect which class it was given and access arguments accordingly.
    """

    overwrite: bool
    path: str
    version: VersionNumber
    level_name: str
    def __init__(self, overwrite, path, version, level_name) -> None: ...

class JavaRawLevelOpenData:
    back_reference: Callable[[], JavaRawLevel | None]
    detach_back_reference: Callable[[], None]
    lock_file: BinaryIO
    lock_time: float
    data_pack: DataPackManager
    dimensions: dict[InternalDimensionId, JavaRawDimension]
    dimension_ids: dict[DimensionId, InternalDimensionId]
    dimensions_lock: RLock
    block_id_override: IdRegistry
    biome_id_override: IdRegistry
    def __init__(
        self,
        raw_level: JavaRawLevel,
        lock_file: BinaryIO,
        lock_time: float,
        data_pack: DataPackManager,
    ) -> None: ...

class JavaRawLevel(RawLevel[JavaRawDimension]):
    def __init__(self, _ikwiad: bool = False) -> None: ...
    @classmethod
    def load(cls, path: str) -> JavaRawLevel: ...
    @classmethod
    def create(cls, args: JavaCreateArgsV1) -> JavaRawLevel: ...
    def is_open(self) -> bool: ...
    def reload(self) -> None:
        """Reload the raw level."""
    opened: Incomplete
    def open(self) -> None:
        """Open the raw level."""
    closed: Incomplete
    def close(self) -> None:
        """Close the raw level."""

    @property
    def path(self) -> str: ...
    @property
    def level_dat(self) -> NamedTag:
        """Get the level.dat file for the world"""

    @level_dat.setter
    def level_dat(self, level_dat: NamedTag) -> None: ...
    @property
    def platform(self) -> str: ...
    @property
    def data_version(self) -> VersionNumber:
        """
        The game data version that the level was last opened in.
        This is used to determine the data format to save in.
        """

    @property
    def modified_time(self) -> float:
        """Unix timestamp of when the level was last modified."""

    @property
    def level_name(self) -> str: ...
    @level_name.setter
    def level_name(self, value: str) -> None: ...
    def dimension_ids(self) -> frozenset[DimensionId]: ...
    def get_dimension(self, dimension_id: DimensionId) -> JavaRawDimension: ...
    def compact(self) -> None:
        """Compact all region files"""

    @property
    def block_id_override(self) -> IdRegistry:
        """
        A two-way map from hard coded numerical block id <-> block string.
        This only stores overridden values. If the value is not present here you should check the translator.
        """

    @property
    def biome_id_override(self) -> IdRegistry:
        """
        A two-way map from hard coded numerical biome id <-> biome string.
        This only stores overridden values. If the value is not present here you should check the translator.
        """
