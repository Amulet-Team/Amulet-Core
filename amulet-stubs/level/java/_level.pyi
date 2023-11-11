import abc
from ._data_pack import DataPack as DataPack, DataPackManager as DataPackManager
from ._dimension import AnvilDimensionManager as AnvilDimensionManager
from PIL import Image
from _typeshed import Incomplete
from amulet.api.data_types import BiomeType as BiomeType, Dimension as Dimension, VersionNumberInt as VersionNumberInt, VersionNumberTuple as VersionNumberTuple
from amulet.block import Block as Block, UniversalAirBlock as UniversalAirBlock
from amulet.level.abc import CompactableLevel as CompactableLevel, CreatableLevel as CreatableLevel, CreateArgsT as CreateArgsT, DiskLevel as DiskLevel, IntArg as IntArg, LevelPrivate as LevelPrivate, LoadableLevel as LoadableLevel, SequenceArg as SequenceArg, StringArg as StringArg
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from amulet.utils.format_utils import check_all_exist as check_all_exist
from amulet_nbt import NamedTag as NamedTag
from typing import Any, NamedTuple, Optional, Sequence, Union

log: Incomplete
InternalDimension = str
OVERWORLD: str
THE_NETHER: str
THE_END: str
DefaultSelection: Incomplete

class DimensionEntry(NamedTuple):
    relative_dimension_path: InternalDimension
    dimension_name: Dimension
    manager: AnvilDimensionManager
    bounds: SelectionGroup
    default_block: Block
    default_biome: BiomeType

class JavaLevelPrivate(LevelPrivate):
    path: Optional[str]
    data_version: Optional[VersionNumberInt]
    root_tag: Optional[NamedTag]
    mcc_support: bool
    dimensions: dict[Union[InternalDimension, Dimension], DimensionEntry]
    data_pack: Optional[DataPackManager]
    __slots__: Incomplete
    level: JavaLevel
    def __init__(self, level: JavaLevel) -> None: ...
    def _close(self) -> None: ...

class JavaLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel, metaclass=abc.ABCMeta):
    __slots__: Incomplete
    _l: JavaLevelPrivate
    _lock_file: Incomplete
    _lock_time: Incomplete
    def __init__(self) -> None: ...
    def _instance_data(self) -> JavaLevelPrivate: ...
    root_tag: Incomplete
    @classmethod
    def create(cls, *, path: str, name: str, version: VersionNumberTuple, overwrite: bool = ..., **kwargs) -> JavaLevel: ...
    @staticmethod
    def create_args() -> dict[str, CreateArgsT]: ...
    @staticmethod
    def can_load(token: Any) -> bool: ...
    @classmethod
    def load(cls, path: str) -> JavaLevel: ...
    def _register_dimension(self, relative_dimension_path: InternalDimension, dimension_name: Optional[Dimension] = ...):
        '''
        Register a new dimension.

        :param relative_dimension_path: The relative path to the dimension directory from the world root.
            "" for the world root.
        :param dimension_name: The name of the dimension shown to the user
        '''
    def _get_dimension_bounds(self, dimension_type_str: Dimension) -> SelectionGroup: ...
    def _open(self) -> None: ...
    def _close(self) -> None: ...
    @property
    def path(self) -> str: ...
    @property
    def thumbnail(self) -> Image.Image: ...
    @property
    def data_pack(self) -> DataPackManager: ...
    @property
    def dimensions(self) -> Sequence[Dimension]: ...
