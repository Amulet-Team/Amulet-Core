from __future__ import annotations

from typing import Any, BinaryIO, NamedTuple, Sequence
import os
import time
import struct
import logging

from PIL import Image
import portalocker
from amulet_nbt import (
    load as load_nbt,
    NamedTag,
    CompoundTag,
    IntTag,
    StringTag,
    ListTag,
)

from amulet.api.data_types import BiomeType
from amulet.data_types import DimensionId
from amulet.block import Block
from amulet.selection import SelectionGroup
from amulet.level.abc import (
    DiskLevel,
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
    LevelOpenData,
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
from amulet.level import register_level_class
from amulet.version import VersionNumber

from amulet.level.java._raw._dimension import AnvilDimensionManager

from ._dimension import JavaDimension
from ._raw import JavaCreateArgsV1, JavaRawLevel
from ..abc._level._level import DimensionT

log = logging.getLogger(__name__)

InternalDimension = str



# class DimensionData(Protocol):
#     name: DimensionId
#     bounds: SelectionGroup
#     default_block: Block
#     default_biome: BiomeType


class DimensionEntry(NamedTuple):
    relative_dimension_path: InternalDimension
    dimension_name: DimensionId
    manager: AnvilDimensionManager
    bounds: SelectionGroup
    default_block: Block
    default_biome: BiomeType


class JavaLevelOpenData(LevelOpenData):
    dimensions: dict[DimensionId | InternalDimension, JavaDimension]

    def __init__(self) -> None:
        super().__init__()
        self.dimensions = {}


class JavaLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel):
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
                level_dat_root = load_nbt(os.path.join(token, "level.dat")).compound
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

    # def _register_dimension(
    #     self,
    #     relative_dimension_path: InternalDimension,
    #     dimension_name: Optional[DimensionId] = None,
    # ):
    #     """
    #     Register a new dimension.
    #
    #     :param relative_dimension_path: The relative path to the dimension directory from the world root.
    #         "" for the world root.
    #     :param dimension_name: The name of the dimension shown to the user
    #     """
    #     if dimension_name is None:
    #         dimension_name: DimensionId = relative_dimension_path
    #
    #     if relative_dimension_path:
    #         path = os.path.join(self.path, relative_dimension_path)
    #     else:
    #         path = self.path
    #
    #     if (
    #         relative_dimension_path not in self._l.dimensions
    #         and dimension_name not in self._l.dimensions
    #     ):
    #         self._l.dimensions[relative_dimension_path] = self._l.dimensions[
    #             dimension_name
    #         ] = DimensionEntry(
    #             relative_dimension_path,
    #             dimension_name,
    #             AnvilDimensionManager(
    #                 path,
    #                 mcc=self._l.mcc_support,
    #                 layers=("region",)
    #                 + ("entities",) * (self._l.data_version >= VersionNumber(2681)),
    #             ),
    #             self._get_dimension_bounds(dimension_name),
    #             UniversalAirBlock,
    #             "universal_minecraft:plains",  # TODO: get this data from somewhere
    #         )

    def reload(self) -> None:
        self.raw.reload()

    def _open(self) -> None:
        self.raw.open()
        self._open_data = JavaLevelOpenData()

    def _close(self) -> None:
        self._o.dimensions.clear()
        self._open_data = None
        self.raw.close()

    @property
    def path(self) -> str:
        return self.raw.path

    @property
    def thumbnail(self) -> Image.Image:
        try:
            return Image.open(os.path.join(self.path, "icon.png"))
        except Exception:
            return super().thumbnail

    @property
    def dimension_ids(self) -> frozenset[DimensionId]:
        return tuple(filter(lambda e: isinstance(e, DimensionId), self._l.dimensions))

    def get_dimension(self, dimension_id: DimensionId) -> JavaDimension:


    @property
    def raw(self) -> JavaRawLevel:
        return self._raw_level

    def compact(self) -> None:
        raise NotImplementedError


register_level_class(JavaLevel)
