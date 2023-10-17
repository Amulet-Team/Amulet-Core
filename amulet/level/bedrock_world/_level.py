from __future__ import annotations

from typing import Any, Iterable, Optional, Union
import os

from amulet.api.data_types import DimensionID
from amulet.level.base_level import (
    BaseLevelPrivate,
    DiskLevel,
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
    CreateArgsT,
    PlayerStorage,
)
from amulet.utils.format_utils import check_all_exist
from amulet.level.base_level import Dimension, metadata

from ._level_dat import BedrockLevelDAT
from ._raw_level import BedrockRawLevel, InternalDimension


class BedrockLevelPrivate(BaseLevelPrivate):
    path: Optional[str]
    level_dat: Optional[BedrockLevelDAT]

    __slots__ = tuple(__annotations__)

    level: BedrockLevel

    def __init__(self, level: BedrockLevel):
        super().__init__(level)
        self.path = None
        self.level_dat = None


class BedrockLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel):
    _dimensions: dict[DimensionID,]
    _raw_level: BedrockRawLevel

    __slots__ = ()

    _d: BedrockLevelPrivate

    def __init__(self):
        super().__init__()
        self._raw_level = BedrockRawLevel(self._d)
        self._dimensions = {}

    def _instance_data(self) -> BedrockLevelPrivate:
        return BedrockLevelPrivate(self)

    @staticmethod
    def create_args() -> dict[str, CreateArgsT]:
        raise NotImplementedError

    @classmethod
    def create(cls, *args, **kwargs) -> BedrockLevel:
        raise NotImplementedError

    @staticmethod
    def can_load(token: Any) -> bool:
        return (
            isinstance(token, str)
            and os.path.isdir(token)
            and check_all_exist(token, "db", "level.dat", "levelname.txt")
        )

    @classmethod
    def load(cls, path: str) -> BedrockLevel:
        """
        >>> level: DiskLevel
        >>> level.thumbnail
        :param path:
        :return:
        """
        self = cls()
        self._d.path = path
        self._d.level_dat = BedrockLevelDAT.from_file(
            os.path.join(self.path, "level.dat")
        )
        return self

    def _open(self):
        raise NotImplementedError

    def _close(self):
        self._dimensions.clear()

    @metadata
    @property
    def path(self) -> str:
        return self._d.path

    @metadata
    @property
    def level_name(self) -> str:
        raise NotImplementedError

    def dimensions(self) -> Iterable[DimensionID]:
        return self.raw.dimensions()

    def get_dimension(self, dimension: Union[DimensionID, InternalDimension]) -> Dimension:
        raise NotImplementedError

    @property
    def raw(self) -> BedrockRawLevel:
        return self._raw_level

    @property
    def player(self) -> PlayerStorage:
        raise NotImplementedError

    def compact(self):
        raise NotImplementedError
