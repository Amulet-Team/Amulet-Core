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
from amulet.utils.signal import Signal

from ._raw_level import BedrockRawLevel, InternalDimension


class BedrockLevelPrivate(BaseLevelPrivate):
    path: Optional[str]

    __slots__ = tuple(__annotations__)

    level: BedrockLevel
    reloaded = Signal()

    def __init__(self, level: BedrockLevel):
        super().__init__(level)
        self.path = None


class BedrockLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel):
    _dimensions: dict[DimensionID,]
    _raw_level: BedrockRawLevel

    __slots__ = ()

    _l: BedrockLevelPrivate

    def __init__(self):
        super().__init__()
        self._raw_level = BedrockRawLevel(self._l)
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
        self._l.path = path
        self._l.reloaded.emit()
        return self

    def reload(self):
        if self.is_open:
            raise RuntimeError("Cannot reload a level when it is open.")
        self._l.reloaded.emit()

    def _open(self):
        raise NotImplementedError

    def _close(self):
        self._dimensions.clear()

    @metadata
    @property
    def path(self) -> str:
        return self._l.path

    @metadata
    @property
    def level_name(self) -> str:
        raise NotImplementedError

    def dimensions(self) -> Iterable[DimensionID]:
        return self.raw.dimensions()

    def get_dimension(
        self, dimension: Union[DimensionID, InternalDimension]
    ) -> Dimension:
        raise NotImplementedError

    @property
    def raw(self) -> BedrockRawLevel:
        return self._raw_level

    @property
    def player(self) -> PlayerStorage:
        raise NotImplementedError

    def compact(self):
        raise NotImplementedError
