from PIL import Image
from __future__ import annotations
from amulet.chunk import Chunk
from amulet.level._load import register_level_class
import amulet.level.abc._level._compactable_level
from amulet.level.abc._level._compactable_level import CompactableLevel
import amulet.level.abc._level._creatable_level
from amulet.level.abc._level._creatable_level import CreatableLevel
import amulet.level.abc._level._disk_level
from amulet.level.abc._level._disk_level import DiskLevel
import amulet.level.abc._level._level
from amulet.level.abc._level._level import LevelOpenData
import amulet.level.abc._level._loadable_level
from amulet.level.abc._level._loadable_level import LoadableLevel
from amulet.level.abc._player_storage import PlayerStorage
from amulet.level.java._dimension import JavaDimension
from amulet.level.java._raw._level import JavaCreateArgsV1
from amulet.level.java._raw._level import JavaRawLevel
from amulet.utils.call_spec._call_spec import BoolArg
from amulet.utils.call_spec._call_spec import CallableArg
from amulet.utils.call_spec._call_spec import DirectoryPathArg
from amulet.utils.call_spec._call_spec import IntArg
from amulet.utils.call_spec._call_spec import PositionalArgs
from amulet.utils.call_spec._call_spec import StringArg
from amulet.utils.call_spec._call_spec import method_spec
from amulet.utils.weakref import DetachableWeakRef
from amulet.version import VersionNumber
from amulet_nbt import read_nbt
from builtins import str as PlatformType
from builtins import str as InternalDimensionId
from builtins import str as DimensionId
import logging as logging
import os as os
import typing
from typing import Any

__all__ = [
    "Any",
    "BoolArg",
    "CallableArg",
    "Chunk",
    "CompactableLevel",
    "CreatableLevel",
    "DetachableWeakRef",
    "DimensionId",
    "DirectoryPathArg",
    "DiskLevel",
    "Image",
    "IntArg",
    "InternalDimensionId",
    "JavaCreateArgsV1",
    "JavaDimension",
    "JavaLevel",
    "JavaLevelOpenData",
    "JavaRawLevel",
    "LevelOpenData",
    "LoadableLevel",
    "PlatformType",
    "PlayerStorage",
    "PositionalArgs",
    "StringArg",
    "VersionNumber",
    "log",
    "logging",
    "method_spec",
    "os",
    "read_nbt",
    "register_level_class",
]

class JavaLevel(
    amulet.level.abc._level._disk_level.DiskLevel,
    amulet.level.abc._level._creatable_level.CreatableLevel,
    amulet.level.abc._level._loadable_level.LoadableLevel,
    amulet.level.abc._level._compactable_level.CompactableLevel,
):
    __slots__: typing.ClassVar[tuple] = "_raw_level"
    @staticmethod
    def can_load(token: typing.Any) -> bool: ...
    @classmethod
    def create(cls, args: JavaCreateArgsV1) -> JavaLevel: ...
    @classmethod
    def load(cls, path: str) -> JavaLevel: ...
    def _JavaLevel__init(self, raw: JavaRawLevel) -> None: ...
    def __init__(self, _ikwiad: bool = False) -> None: ...
    def _close(self) -> None: ...
    def _open(self) -> None: ...
    def compact(self) -> None: ...
    def dimension_ids(self) -> frozenset[DimensionId]: ...
    def get_dimension(
        self, dimension_id: DimensionId | InternalDimensionId
    ) -> JavaDimension: ...
    def reload(self) -> None: ...
    def save(self) -> None: ...
    @property
    def level_name(self) -> str: ...
    @property
    def max_game_version(self) -> VersionNumber: ...
    @property
    def modified_time(self) -> float: ...
    @property
    def native_chunk_class(self) -> Type[Chunk]: ...
    @property
    def path(self) -> str: ...
    @property
    def platform(self) -> PlatformType: ...
    @property
    def player(self) -> PlayerStorage: ...
    @property
    def raw(self) -> JavaRawLevel: ...
    @property
    def thumbnail(self) -> Image.Image: ...

class JavaLevelOpenData(amulet.level.abc._level._level.LevelOpenData):
    def __init__(self, level: JavaLevel) -> None: ...

log: logging.Logger  # value = <Logger amulet.level.java._level (INFO)>
