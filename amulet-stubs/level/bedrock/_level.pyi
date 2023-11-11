import abc
from ._raw import BedrockLevelDAT as BedrockLevelDAT, BedrockRawLevel as BedrockRawLevel, InternalDimension as InternalDimension
from PIL import Image
from _typeshed import Incomplete
from amulet.api.data_types import DimensionID as DimensionID, PlatformType as PlatformType
from amulet.api.errors import ObjectWriteError as ObjectWriteError
from amulet.level.abc import CompactableLevel as CompactableLevel, CreatableLevel as CreatableLevel, CreateArgsT as CreateArgsT, Dimension as Dimension, DiskLevel as DiskLevel, LevelPrivate as LevelPrivate, LoadableLevel as LoadableLevel, PlayerStorage as PlayerStorage
from amulet.utils.format_utils import check_all_exist as check_all_exist
from amulet.utils.signal import Signal as Signal
from amulet.version import SemanticVersion as SemanticVersion
from typing import Any, Optional, Union

class BedrockLevelPrivate(LevelPrivate):
    path: Optional[str]
    __slots__: Incomplete
    level: BedrockLevel
    reloaded: Incomplete
    def __init__(self, level: BedrockLevel) -> None: ...

class BedrockLevel(DiskLevel[BedrockLevelPrivate], CreatableLevel, LoadableLevel, CompactableLevel, metaclass=abc.ABCMeta):
    _dimensions: dict[Union[DimensionID, InternalDimension], Dimension]
    _raw_level: BedrockRawLevel
    __slots__: Incomplete
    def __init__(self) -> None: ...
    def _instance_data(self) -> BedrockLevelPrivate: ...
    @staticmethod
    def create_args() -> dict[str, CreateArgsT]: ...
    @classmethod
    def create(cls, *, overwrite: bool, path: str, version: tuple[int, int, int, int, int], level_name: str) -> BedrockLevel: ...
    @staticmethod
    def can_load(token: Any) -> bool: ...
    @classmethod
    def load(cls, path: str) -> BedrockLevel:
        """Create a new instance from the level at the given directory."""
    def reload(self) -> None:
        """
        Reload the level metadata inplace.
        The level must be closed when this is called.
        """
    def _open(self) -> None: ...
    def _close(self) -> None: ...
    @property
    def path(self) -> str: ...
    @property
    def level_name(self) -> str: ...
    @property
    def thumbnail(self) -> Image.Image: ...
    @property
    def platform(self) -> PlatformType: ...
    @property
    def max_game_version(self) -> SemanticVersion: ...
    def dimensions(self) -> frozenset[DimensionID]: ...
    def get_dimension(self, dimension: Union[DimensionID, InternalDimension]) -> Dimension: ...
    @property
    def raw(self) -> BedrockRawLevel: ...
    @property
    def player(self) -> PlayerStorage: ...
    def compact(self) -> None: ...
