from __future__ import annotations

from typing import Any, Optional, Union
import os
import shutil
import time

from PIL import Image
from leveldb import LevelDB
from amulet_nbt import CompoundTag, IntTag, ListTag, LongTag, StringTag

from amulet.api.data_types import DimensionID, PlatformType, VersionNumberTuple
from amulet.level.base_level import (
    BaseLevelPrivate,
    DiskLevel,
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
    CreateArgsT,
    PlayerStorage,
    Dimension,
    metadata,
)
from amulet.api.errors import ObjectWriteError
from amulet.utils.format_utils import check_all_exist
from amulet.utils.signal import Signal

from ._raw_level import BedrockRawLevel, InternalDimension
from ._level_dat import BedrockLevelDAT


class BedrockLevelPrivate(BaseLevelPrivate):
    path: Optional[str]

    __slots__ = tuple(__annotations__)

    level: BedrockLevel
    reloaded = Signal()

    def __init__(self, level: BedrockLevel):
        super().__init__(level)
        self.path = None


class BedrockLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel):
    _dimensions: dict[Union[DimensionID, InternalDimension], Dimension]
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
    def create(
        cls,
        *,
        overwrite: bool,
        path: str,
        version: tuple[int, int, int, int, int],
        level_name: str,
    ) -> BedrockLevel:
        if os.path.isdir(path):
            if overwrite:
                shutil.rmtree(path)
            else:
                raise ObjectWriteError(f"A directory already exists at the path {path}")
        os.makedirs(path, exist_ok=True)

        root = CompoundTag()
        root["StorageVersion"] = IntTag(8)
        root["lastOpenedWithVersion"] = ListTag([IntTag(i) for i in version])
        root["Generator"] = IntTag(1)
        root["LastPlayed"] = LongTag(int(time.time()))
        root["LevelName"] = StringTag(level_name)
        BedrockLevelDAT(root, level_dat_version=9).save_to(
            os.path.join(path, "level.dat")
        )

        with open(os.path.join(path, "levelname.txt"), "w", encoding="utf-8") as f:
            f.write(level_name)

        db = LevelDB(os.path.join(path, "db"), True)
        db.close()

        return cls.load(path)

    @staticmethod
    def can_load(token: Any) -> bool:
        return (
            isinstance(token, str)
            and os.path.isdir(token)
            and check_all_exist(token, "db", "level.dat", "levelname.txt")
        )

    @classmethod
    def load(cls, path: str) -> BedrockLevel:
        """Create a new instance from the level at the given directory."""
        self = cls()
        self._l.path = path
        self._l.reloaded.emit()
        return self

    def reload(self):
        """
        Reload the level metadata inplace.
        The level must be closed when this is called.
        """
        if self.is_open:
            raise RuntimeError("Cannot reload a level when it is open.")
        self._l.reloaded.emit()

    def _open(self):
        pass

    def _close(self):
        self._dimensions.clear()

    @metadata
    @property
    def path(self) -> str:
        return self._l.path

    @metadata
    @property
    def level_name(self) -> str:
        try:
            return self.raw.level_dat.compound.get_string("LevelName").py_str
        except Exception:
            return "Unknown level name"

    @metadata
    @property
    def thumbnail(self) -> Image.Image:
        try:
            return Image.open(os.path.join(self.path, "world_icon.jpeg"))
        except Exception:
            return super().thumbnail

    @property
    def platform(self) -> PlatformType:
        return "bedrock"

    @property
    def version(self) -> VersionNumberTuple:
        return self.raw.max_game_version

    def dimensions(self) -> frozenset[DimensionID]:
        return self.raw.dimensions()

    def get_dimension(
        self, dimension: Union[DimensionID, InternalDimension]
    ) -> Dimension:
        if dimension not in self._dimensions:
            raw_dimension = self.raw.get_dimension(dimension)
            public_dimension = raw_dimension.dimension
            internal_dimension = raw_dimension.internal_dimension
            self._dimensions[internal_dimension] = self._dimensions[
                public_dimension
            ] = Dimension(self._l, public_dimension)
        return self._dimensions[dimension]

    @property
    def raw(self) -> BedrockRawLevel:
        return self._raw_level

    @property
    def player(self) -> PlayerStorage:
        raise NotImplementedError

    def compact(self):
        self.raw.level_db.compact()
