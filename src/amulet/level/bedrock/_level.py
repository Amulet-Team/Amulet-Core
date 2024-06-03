from __future__ import annotations

from typing import Any, Union, Type, Callable
import os

from PIL import Image

from amulet.version import VersionNumber, PlatformType
from amulet.data_types import DimensionId
from amulet.level import register_level_class
from amulet.level.abc import (
    LevelOpenData,
    DiskLevel,
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
    PlayerStorage,
)
from amulet.utils.format_utils import check_all_exist
from amulet.utils.call_spec import (
    StringArg,
    IntArg,
    CallableArg,
    BoolArg,
    DirectoryPathArg,
    PositionalArgs,
    method_spec,
)
from amulet.utils.weakref import DetachableWeakRef

from ._raw import BedrockRawLevel, InternalDimension, BedrockCreateArgsV1
from ._dimension import BedrockDimension
from ...chunk import Chunk


class BedrockLevelOpenData(LevelOpenData):
    back_reference: Callable[[], BedrockLevel | None]
    detach_back_reference: Callable[[], None]
    dimensions: dict[Union[DimensionId, InternalDimension], BedrockDimension]

    def __init__(self, level: BedrockLevel) -> None:
        super().__init__()
        self.back_reference, self.detach_back_reference = DetachableWeakRef.new(level)
        self.dimensions = {}


class BedrockLevel(
    DiskLevel[BedrockLevelOpenData, BedrockDimension, BedrockRawLevel],
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
):
    def save(self) -> None:
        pass

    @property
    def native_chunk_class(self) -> Type[Chunk]:
        raise NotImplementedError

    _raw_level: BedrockRawLevel

    __slots__ = ("_raw_level",)

    def __init__(self, _ikwiad: bool = False) -> None:
        if not _ikwiad:
            raise RuntimeError(
                "BedrockLevel cannot be directly initialised. Use create or load classmethod."
            )
        super().__init__()

    def __init(self, raw: BedrockRawLevel) -> None:
        self._raw_level = raw
        self._raw_level.opened.connect(self.open)
        self._raw_level.closed.connect(self.close)

    @classmethod
    @method_spec(
        CallableArg(
            BedrockCreateArgsV1,
            BoolArg(True),
            DirectoryPathArg(),
            CallableArg(
                VersionNumber,
                PositionalArgs(IntArg(min_value=0), (IntArg(1), IntArg(20))),
            ),
            StringArg("New World"),
        )
    )
    def create(cls, args: BedrockCreateArgsV1) -> BedrockLevel:
        raw = BedrockRawLevel.create(args)
        self = cls(True)
        self.__init(raw)
        return self

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
        raw = BedrockRawLevel.load(path)
        self = cls(True)
        self.__init(raw)
        return self

    def reload(self) -> None:
        """
        Reload the level metadata inplace.
        The level must be closed when this is called.
        """
        self.raw.reload()

    def _open(self) -> None:
        self.raw.open()
        self._open_data = BedrockLevelOpenData(self)

    def _close(self) -> None:
        self._o.detach_back_reference()
        self._open_data = None
        self.raw.close()

    @property
    def path(self) -> str:
        return self.raw.path

    @property
    def level_name(self) -> str:
        try:
            level_name_tag = self.raw.level_dat.compound.get_string("LevelName")
            assert level_name_tag is not None
            return level_name_tag.py_str
        except Exception:
            return "Unknown level name"

    @property
    def modified_time(self) -> float:
        return self.raw.modified_time

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
    def max_game_version(self) -> VersionNumber:
        return self.raw.version

    def dimension_ids(self) -> frozenset[DimensionId]:
        return self.raw.dimension_ids()

    def get_dimension(
        self, dimension_id: Union[DimensionId, InternalDimension]
    ) -> BedrockDimension:
        dimensions = self._o.dimensions
        if dimension_id not in dimensions:
            raw_dimension = self.raw.get_dimension(dimension_id)
            public_dimension_id = raw_dimension.dimension_id
            internal_dimension_id = raw_dimension.internal_dimension_id
            dimensions[internal_dimension_id] = dimensions[public_dimension_id] = (
                BedrockDimension(self._o.back_reference, public_dimension_id)
            )
        return dimensions[dimension_id]

    @property
    def raw(self) -> BedrockRawLevel:
        return self._raw_level

    @property
    def player(self) -> PlayerStorage:
        raise NotImplementedError

    def compact(self) -> None:
        self.raw.level_db.compact()


register_level_class(BedrockLevel)
