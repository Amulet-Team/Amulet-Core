from __future__ import annotations

from typing import Any, Type, Callable
import os
import logging

from PIL import Image
from amulet_nbt import (
    read_nbt,
)

from amulet.data_types import DimensionId
from amulet.level.abc import (
    DiskLevel,
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
    LevelOpenData,
    PlayerStorage,
)
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
from amulet.level import register_level_class
from amulet.version import VersionNumber, PlatformType

from ._dimension import JavaDimension
from ._raw import JavaCreateArgsV1, JavaRawLevel, InternalDimensionId
from amulet.chunk import Chunk

log = logging.getLogger(__name__)


class JavaLevelOpenData(LevelOpenData):
    back_reference: Callable[[], JavaLevel | None]
    detach_back_reference: Callable[[], None]
    dimensions: dict[DimensionId | InternalDimensionId, JavaDimension]

    def __init__(self, level: JavaLevel) -> None:
        super().__init__()
        self.back_reference, self.detach_back_reference = DetachableWeakRef.new(level)
        self.dimensions = {}


class JavaLevel(
    DiskLevel[JavaLevelOpenData, JavaDimension, JavaRawLevel],
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
):
    __slots__ = ("_raw_level",)

    def __init__(self, _ikwiad: bool = False) -> None:
        if not _ikwiad:
            raise RuntimeError(
                "BedrockRawLevel must be constructed using the create or load classmethod."
            )
        super().__init__()

    def __init(self, raw: JavaRawLevel) -> None:
        self._raw_level = raw
        self._raw_level.opened.connect(self.open)
        self._raw_level.closed.connect(self.close)

    @classmethod
    @method_spec(
        CallableArg(
            JavaCreateArgsV1,
            BoolArg(True),
            DirectoryPathArg(),
            CallableArg(
                VersionNumber,
                PositionalArgs(IntArg(min_value=0), (IntArg(1), IntArg(20))),
            ),
            StringArg("New World"),
        )
    )
    def create(cls, args: JavaCreateArgsV1) -> JavaLevel:
        raw = JavaRawLevel.create(args)
        self = cls(True)
        self.__init(raw)
        return self

    @staticmethod
    def can_load(token: Any) -> bool:
        if (
            isinstance(token, str)
            and os.path.isdir(token)
            and os.path.isfile(os.path.join(token, "level.dat"))
        ):
            try:
                level_dat_root = read_nbt(os.path.join(token, "level.dat")).compound
            except Exception:
                pass
            else:
                return "Data" in level_dat_root and "FML" not in level_dat_root
        return False

    @classmethod
    def load(cls, path: str) -> JavaLevel:
        raw = JavaRawLevel.load(path)
        self = cls(True)
        self.__init(raw)
        return self

    def reload(self) -> None:
        self.raw.reload()

    def _open(self) -> None:
        self.raw.open()
        self._open_data = JavaLevelOpenData(self)

    def _close(self) -> None:
        self._o.detach_back_reference()
        self._open_data = None
        self.raw.close()

    def save(self) -> None:
        raise NotImplementedError

    @property
    def platform(self) -> PlatformType:
        return self.raw.platform

    @property
    def max_game_version(self) -> VersionNumber:
        return self.raw.data_version

    @property
    def level_name(self) -> str:
        return self.raw.level_name

    @property
    def modified_time(self) -> float:
        return self.raw.modified_time

    @property
    def path(self) -> str:
        return self.raw.path

    @property
    def thumbnail(self) -> Image.Image:
        try:
            return Image.open(os.path.join(self.path, "icon.png"))
        except Exception:
            return super().thumbnail

    def dimension_ids(self) -> frozenset[DimensionId]:
        return self.raw.dimension_ids()

    def get_dimension(
        self, dimension_id: DimensionId | InternalDimensionId
    ) -> JavaDimension:
        if dimension_id not in self._o.dimensions:
            raw_dimension = self.raw.get_dimension(dimension_id)
            self._o.dimensions[raw_dimension.dimension_id] = self._o.dimensions[
                raw_dimension.relative_path
            ] = JavaDimension(self._o.back_reference, raw_dimension.dimension_id)
        return self._o.dimensions[dimension_id]

    @property
    def player(self) -> PlayerStorage:
        raise NotImplementedError

    @property
    def native_chunk_class(self) -> Type[Chunk]:
        raise NotImplementedError

    @property
    def raw(self) -> JavaRawLevel:
        return self._raw_level

    def compact(self) -> None:
        self.raw.compact()


register_level_class(JavaLevel)
