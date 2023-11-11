from .data_pack import DataPack as DataPack, DataPackManager as DataPackManager
from .dimension import AnvilDimensionManager as AnvilDimensionManager, ChunkDataType as ChunkDataType
from _typeshed import Incomplete
from amulet.api import level as api_level
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, ChunkCoordinates as ChunkCoordinates, Dimension as Dimension, DimensionCoordinates as DimensionCoordinates, PlatformType as PlatformType, VersionNumberInt as VersionNumberInt
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ChunkLoadError as ChunkLoadError, DimensionDoesNotExist as DimensionDoesNotExist, ObjectWriteError as ObjectWriteError, PlayerDoesNotExist as PlayerDoesNotExist
from amulet.api.wrapper import DefaultSelection as DefaultSelection, WorldFormatWrapper as WorldFormatWrapper
from amulet.level.interfaces.chunk.anvil.base_anvil_interface import BaseAnvilInterface as BaseAnvilInterface
from amulet.player import LOCAL_PLAYER as LOCAL_PLAYER, Player as Player
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from amulet.utils.format_utils import check_all_exist as check_all_exist
from amulet_nbt import CompoundTag, NamedTag
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple, Union

log: Incomplete
InternalDimension = str
OVERWORLD: str
THE_NETHER: str
THE_END: str

class AnvilFormat(WorldFormatWrapper[VersionNumberInt]):
    """
    This FormatWrapper class exists to interface with the Java world format.
    """
    _platform: str
    _root_tag: Incomplete
    _levels: Incomplete
    _dimension_name_map: Incomplete
    _mcc_support: Incomplete
    _lock_time: Incomplete
    _lock: Incomplete
    _data_pack: Incomplete
    def __init__(self, path: str) -> None:
        """
        Construct a new instance of :class:`AnvilFormat`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
    def _shallow_load(self) -> None: ...
    _world_image_path: Incomplete
    def _load_level_dat(self) -> None:
        """Load the level.dat file and check the image file"""
    @staticmethod
    def is_valid(token) -> bool: ...
    @staticmethod
    def valid_formats() -> Dict[PlatformType, Tuple[bool, bool]]: ...
    _version: Incomplete
    @property
    def version(self) -> VersionNumberInt:
        """The data version number that the world was last opened in. eg 2578"""
    def _get_version(self) -> VersionNumberInt: ...
    @property
    def root_tag(self) -> NamedTag:
        """The level.dat data for the level."""
    @root_tag.setter
    def root_tag(self, root_tag: Union[NamedTag, CompoundTag]): ...
    @property
    def level_name(self) -> str: ...
    @level_name.setter
    def level_name(self, value: str): ...
    @property
    def last_played(self) -> int: ...
    @property
    def game_version_string(self) -> str: ...
    @property
    def data_pack(self) -> DataPackManager: ...
    @property
    def dimensions(self) -> List[Dimension]: ...
    def _register_dimension(self, relative_dimension_path: InternalDimension, dimension_name: Optional[Dimension] = ...):
        '''
        Register a new dimension.

        :param relative_dimension_path: The relative path to the dimension directory from the world root. "" for the world root.
        :param dimension_name: The name of the dimension shown to the user
        '''
    def _get_dimenion_bounds(self, dimension_type_str: Dimension) -> SelectionGroup: ...
    def _get_interface(self, raw_chunk_data: Optional[Any] = ...) -> Interface: ...
    def _get_interface_key(self, raw_chunk_data: Optional[ChunkDataType] = ...) -> Tuple[str, int]: ...
    def _decode(self, interface: BaseAnvilInterface, dimension: Dimension, cx: int, cz: int, raw_chunk_data: ChunkDataType) -> Tuple[Chunk, AnyNDArray]: ...
    def _encode(self, interface: BaseAnvilInterface, chunk: Chunk, dimension: Dimension, chunk_palette: AnyNDArray) -> ChunkDataType: ...
    _is_open: bool
    _has_lock: bool
    def _reload_world(self) -> None: ...
    def _open(self) -> None:
        """Open the database for reading and writing"""
    def _create(self, overwrite: bool, bounds: Union[SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None] = ..., **kwargs): ...
    @property
    def has_lock(self) -> bool: ...
    def pre_save_operation(self, level: api_level.BaseLevel) -> Generator[float, None, bool]: ...
    @staticmethod
    def _calculate_height(level: api_level.BaseLevel, chunks: List[DimensionCoordinates]) -> Generator[float, None, bool]:
        """Calculate the height values for chunks."""
    @staticmethod
    def _calculate_light(level: api_level.BaseLevel, chunks: List[DimensionCoordinates]) -> Generator[float, None, bool]:
        """Calculate the height values for chunks."""
    def _save(self) -> None:
        """Save the data back to the disk database"""
    def _close(self) -> None:
        """Close the disk database"""
    def unload(self) -> None: ...
    def _has_dimension(self, dimension: Dimension): ...
    def _get_dimension(self, dimension: Dimension): ...
    def all_chunk_coords(self, dimension: Dimension) -> Iterable[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool: ...
    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        """Delete a chunk from a given dimension"""
    def put_raw_chunk_data(self, cx: int, cz: int, data: NamedTag, dimension: Dimension):
        """
        Commit the raw chunk data to the FormatWrapper cache.

        Call :meth:`save` to push all the cache data to the level.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param data: The raw data to commit to the level.
        :param dimension: The dimension to load the data from.
        """
    def _put_raw_chunk_data(self, cx: int, cz: int, data: ChunkDataType, dimension: Dimension): ...
    def get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> NamedTag:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
    def _legacy_get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> NamedTag: ...
    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> ChunkDataType:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
    def all_player_ids(self) -> Iterable[str]:
        """
        Returns a generator of all player ids that are present in the level
        """
    def has_player(self, player_id: str) -> bool: ...
    def _load_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
    def _get_raw_player_data(self, player_id: str) -> CompoundTag: ...
