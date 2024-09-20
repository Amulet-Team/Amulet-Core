from typing import Any, Callable

from _typeshed import Incomplete
from amulet.chunk import Chunk as Chunk
from amulet.data_types import DimensionId as DimensionId
from amulet.level import register_level_class as register_level_class
from amulet.level.abc import CompactableLevel as CompactableLevel
from amulet.level.abc import CreatableLevel as CreatableLevel
from amulet.level.abc import DiskLevel as DiskLevel
from amulet.level.abc import LevelOpenData as LevelOpenData
from amulet.level.abc import LoadableLevel as LoadableLevel
from amulet.level.abc import PlayerStorage as PlayerStorage
from amulet.utils.call_spec import BoolArg as BoolArg
from amulet.utils.call_spec import CallableArg as CallableArg
from amulet.utils.call_spec import DirectoryPathArg as DirectoryPathArg
from amulet.utils.call_spec import IntArg as IntArg
from amulet.utils.call_spec import PositionalArgs as PositionalArgs
from amulet.utils.call_spec import StringArg as StringArg
from amulet.utils.call_spec import method_spec as method_spec
from amulet.utils.weakref import DetachableWeakRef as DetachableWeakRef
from amulet.version import PlatformType as PlatformType
from amulet.version import VersionNumber as VersionNumber
from PIL import Image

from ._dimension import JavaDimension as JavaDimension
from ._raw import InternalDimensionId as InternalDimensionId
from ._raw import JavaCreateArgsV1 as JavaCreateArgsV1
from ._raw import JavaRawLevel as JavaRawLevel

log: Incomplete

class JavaLevelOpenData(LevelOpenData):
    back_reference: Callable[[], JavaLevel | None]
    detach_back_reference: Callable[[], None]
    dimensions: dict[DimensionId | InternalDimensionId, JavaDimension]
    def __init__(self, level: JavaLevel) -> None: ...

class JavaLevel(
    DiskLevel[JavaLevelOpenData, JavaDimension, JavaRawLevel],
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
):
    def __init__(self, _ikwiad: bool = False) -> None: ...
    @classmethod
    def create(cls, args: JavaCreateArgsV1) -> JavaLevel: ...
    @staticmethod
    def can_load(token: Any) -> bool: ...
    @classmethod
    def load(cls, path: str) -> JavaLevel: ...
    def reload(self) -> None: ...
    def save(self) -> None: ...
    @property
    def platform(self) -> PlatformType: ...
    @property
    def max_game_version(self) -> VersionNumber: ...
    @property
    def level_name(self) -> str: ...
    @property
    def modified_time(self) -> float: ...
    @property
    def path(self) -> str: ...
    @property
    def thumbnail(self) -> Image.Image: ...
    def dimension_ids(self) -> frozenset[DimensionId]: ...
    def get_dimension(
        self, dimension_id: DimensionId | InternalDimensionId
    ) -> JavaDimension: ...
    @property
    def player(self) -> PlayerStorage: ...
    @property
    def native_chunk_class(self) -> type[Chunk]: ...
    @property
    def raw(self) -> JavaRawLevel: ...
    def compact(self) -> None: ...
