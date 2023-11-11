from .interface import Construction0Interface as Construction0Interface, ConstructionInterface as ConstructionInterface
from .section import ConstructionSection as ConstructionSection
from .util import find_fitting_array_type as find_fitting_array_type, pack_palette as pack_palette, parse_block_entities as parse_block_entities, parse_entities as parse_entities, serialise_block_entities as serialise_block_entities, serialise_entities as serialise_entities, unpack_palette as unpack_palette
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, ChunkCoordinates as ChunkCoordinates, Dimension as Dimension, PlatformType as PlatformType, VersionNumberAny as VersionNumberAny, VersionNumberTuple as VersionNumberTuple
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ObjectWriteError as ObjectWriteError
from amulet.api.wrapper import Interface as Interface, StructureFormatWrapper as StructureFormatWrapper, Translator as Translator
from amulet.palette import BlockPalette as BlockPalette
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from typing import Any, BinaryIO, Dict, Iterable, List, Optional, Tuple, Union

log: Incomplete
construction_0_interface: Incomplete
INT_STRUCT: Incomplete
SECTION_ENTRY_TYPE: Incomplete
magic_num: bytes
magic_num_len: Incomplete
max_format_version: int
max_section_version: int

class ConstructionFormatWrapper(StructureFormatWrapper[VersionNumberTuple]):
    """
    This FormatWrapper class exists to interface with the construction format.
    """
    _format_version: int
    _section_version: int
    _chunk_to_section: Dict[Tuple[int, int], List[ConstructionSection]]
    _selection_boxes: List[SelectionBox]
    _chunk_to_box: Dict[Tuple[int, int], List[SelectionBox]]
    def __init__(self, path: str) -> None:
        """
        Construct a new instance of :class:`ConstructionFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
    _platform: Incomplete
    _version: Incomplete
    def _shallow_load(self): ...
    _has_disk_data: bool
    def _create(self, overwrite: bool, bounds: Union[SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None] = ..., format_version=..., section_version=..., **kwargs): ...
    def _populate_chunk_to_box(self) -> None: ...
    def open_from(self, f: BinaryIO): ...
    @property
    def multi_selection(self) -> bool: ...
    @staticmethod
    def is_valid(token) -> bool: ...
    @staticmethod
    def valid_formats() -> Dict[PlatformType, Tuple[bool, bool]]: ...
    @property
    def extensions(self) -> Tuple[str, ...]: ...
    def _get_interface(self, raw_chunk_data: Optional[Any] = ...) -> Construction0Interface: ...
    def _get_interface_and_translator(self, raw_chunk_data: Incomplete | None = ...) -> Tuple['Interface', 'Translator', VersionNumberAny]: ...
    def save_to(self, f: BinaryIO): ...
    def _close(self) -> None:
        """Close the disk database"""
    def unload(self) -> None: ...
    def all_chunk_coords(self, dimension: Optional[Dimension] = ...) -> Iterable[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool: ...
    def _pack(self, chunk: Chunk, translator: Translator, chunk_version: VersionNumberAny) -> Tuple['Chunk', AnyNDArray]: ...
    def _encode(self, interface: ConstructionInterface, chunk: Chunk, dimension: Dimension, chunk_palette: AnyNDArray): ...
    def _unpack(self, translator: Translator, game_version: VersionNumberAny, chunk: Chunk, chunk_palette: AnyNDArray) -> Chunk: ...
    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = ...): ...
    def _put_raw_chunk_data(self, cx: int, cz: int, data: List[ConstructionSection], dimension: Optional[Dimension] = ...): ...
    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Optional[Dimension] = ...) -> List[ConstructionSection]:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
