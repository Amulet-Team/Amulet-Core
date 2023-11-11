from .chunk import MCStructureChunk as MCStructureChunk
from PyMCTranslate import TranslationManager as TranslationManager
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, PlatformType as PlatformType, VersionIdentifierType as VersionIdentifierType, VersionNumberAny as VersionNumberAny, VersionNumberTuple as VersionNumberTuple
from amulet.api.wrapper import EntityCoordType as EntityCoordType, EntityIDType as EntityIDType, Interface as Interface, Translator as Translator
from amulet.block import Block as Block
from amulet.level.loader import Translators as Translators
from amulet.selection import SelectionBox as SelectionBox
from typing import Any, Tuple

class MCStructureInterface(Interface):
    _entity_id_type: Incomplete
    _entity_coord_type: Incomplete
    _block_entity_id_type: Incomplete
    _block_entity_coord_type: Incomplete
    def is_valid(self, key: Tuple) -> bool: ...
    def decode(self, cx: int, cz: int, data: MCStructureChunk) -> Tuple['Chunk', AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: Raw chunk data provided by the format.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
    def encode(self, chunk: Chunk, palette: AnyNDArray, max_world_version: VersionIdentifierType, box: SelectionBox) -> MCStructureChunk:
        """
        Take a version-specific chunk and encode it to raw data for the format to store.
        :param chunk: The already translated version-specfic chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param box: The volume of the chunk to pack.
        :return: Raw data to be stored by the Format.
        """
    def get_translator(self, max_world_version: Tuple[PlatformType, VersionNumberTuple], data: Any = ..., translation_manager: TranslationManager = ...) -> Tuple['Translator', VersionNumberAny]: ...
