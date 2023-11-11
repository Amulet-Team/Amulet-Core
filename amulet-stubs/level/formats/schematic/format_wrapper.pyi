from .chunk import SchematicChunk as SchematicChunk
from .interface import BedrockSchematicInterface as BedrockSchematicInterface, JavaSchematicInterface as JavaSchematicInterface, SchematicInterface as SchematicInterface
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, ChunkCoordinates as ChunkCoordinates, Dimension as Dimension, PlatformType as PlatformType, PointCoordinates as PointCoordinates, VersionNumberAny as VersionNumberAny, VersionNumberTuple as VersionNumberTuple
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ObjectReadError as ObjectReadError, ObjectWriteError as ObjectWriteError
from amulet.api.wrapper import Interface as Interface, StructureFormatWrapper as StructureFormatWrapper, Translator as Translator
from amulet.palette import BlockPalette as BlockPalette
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from typing import BinaryIO, Dict, Iterable, Optional, Tuple, Union

java_interface: Incomplete
bedrock_interface: Incomplete

def _is_schematic(path: str):
    """Check if a file is actually a sponge schematic file."""

class SchematicFormatWrapper(StructureFormatWrapper[VersionNumberTuple]):
    """
    This FormatWrapper class exists to interface with the legacy schematic structure format.
    """
    _chunks: Incomplete
    def __init__(self, path: str) -> None:
        """
        Construct a new instance of :class:`SchematicFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
    def _shallow_load(self) -> None: ...
    _version: Incomplete
    _platform: str
    _has_disk_data: bool
    def _create(self, overwrite: bool, bounds: Union[SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None] = ..., **kwargs): ...
    def open_from(self, f: BinaryIO): ...
    @staticmethod
    def is_valid(token) -> bool: ...
    @staticmethod
    def valid_formats() -> Dict[PlatformType, Tuple[bool, bool]]: ...
    @property
    def extensions(self) -> Tuple[str, ...]: ...
    def _get_interface(self, raw_chunk_data: Incomplete | None = ...) -> SchematicInterface: ...
    def _get_interface_and_translator(self, raw_chunk_data: Incomplete | None = ...) -> Tuple['Interface', 'Translator', VersionNumberAny]: ...
    def save_to(self, f: BinaryIO): ...
    def _close(self) -> None:
        """Close the disk database"""
    def unload(self) -> None: ...
    def all_chunk_coords(self, dimension: Optional[Dimension] = ...) -> Iterable[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool: ...
    def _pack(self, chunk: Chunk, translator: Translator, chunk_version: VersionNumberAny) -> Tuple['Chunk', AnyNDArray]: ...
    def _encode(self, interface: SchematicInterface, chunk: Chunk, dimension: Dimension, chunk_palette: AnyNDArray): ...
    def _unpack(self, translator: Translator, game_version: VersionNumberAny, chunk: Chunk, chunk_palette: AnyNDArray) -> Chunk: ...
    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = ...): ...
    def _put_raw_chunk_data(self, cx: int, cz: int, section: SchematicChunk, dimension: Optional[Dimension] = ...): ...
    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Optional[Dimension] = ...) -> SchematicChunk:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
