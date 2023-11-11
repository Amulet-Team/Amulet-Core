from .chunk import MCStructureChunk as MCStructureChunk
from .interface import MCStructureInterface as MCStructureInterface
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, ChunkCoordinates as ChunkCoordinates, Dimension as Dimension, PlatformType as PlatformType, VersionNumberAny as VersionNumberAny, VersionNumberTuple as VersionNumberTuple
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ObjectWriteError as ObjectWriteError
from amulet.api.wrapper import Interface as Interface, StructureFormatWrapper as StructureFormatWrapper, Translator as Translator
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from amulet.utils.numpy_helpers import brute_sort_objects_no_hash as brute_sort_objects_no_hash
from typing import BinaryIO, Dict, Iterable, Optional, Tuple, Union

mcstructure_interface: Incomplete

class MCStructureFormatWrapper(StructureFormatWrapper[VersionNumberTuple]):
    """
    This FormatWrapper class exists to interface with the Bedrock mcstructure structure block format.
    """
    _chunks: Incomplete
    def __init__(self, path: str) -> None:
        """
        Construct a new instance of :class:`MCStructureFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
    _platform: Incomplete
    _version: Incomplete
    _has_disk_data: bool
    def _create(self, overwrite: bool, bounds: Union[SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None] = ..., **kwargs): ...
    def _shallow_load(self) -> None: ...
    def open_from(self, f: BinaryIO): ...
    @staticmethod
    def is_valid(token) -> bool: ...
    @staticmethod
    def valid_formats() -> Dict[PlatformType, Tuple[bool, bool]]: ...
    @property
    def extensions(self) -> Tuple[str, ...]: ...
    def _get_interface(self, raw_chunk_data: Incomplete | None = ...) -> MCStructureInterface: ...
    def _get_interface_and_translator(self, raw_chunk_data: Incomplete | None = ...) -> Tuple['Interface', 'Translator', VersionNumberAny]: ...
    def save_to(self, f: BinaryIO): ...
    def _close(self) -> None:
        """Close the disk database"""
    def unload(self) -> None: ...
    def all_chunk_coords(self, dimension: Optional[Dimension] = ...) -> Iterable[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool: ...
    def _encode(self, interface: MCStructureInterface, chunk: Chunk, dimension: Dimension, chunk_palette: AnyNDArray): ...
    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = ...): ...
    def _put_raw_chunk_data(self, cx: int, cz: int, section: MCStructureChunk, dimension: Optional[Dimension] = ...): ...
    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Optional[Dimension] = ...) -> MCStructureChunk:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
