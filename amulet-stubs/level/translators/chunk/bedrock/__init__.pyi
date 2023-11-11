from PyMCTranslate import TranslationManager as TranslationManager
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, BedrockInterfaceBlockType as BedrockInterfaceBlockType, BlockCoordinates as BlockCoordinates, GetBlockCallback as GetBlockCallback, GetChunkCallback as GetChunkCallback, TranslateBlockCallbackReturn as TranslateBlockCallbackReturn, TranslateEntityCallbackReturn as TranslateEntityCallbackReturn, VersionIdentifierType as VersionIdentifierType, VersionNumberAny as VersionNumberAny, VersionNumberTuple as VersionNumberTuple
from amulet.api.wrapper.chunk.translator import Translator as Translator
from amulet.block import Block as Block
from amulet.entity import Entity as Entity
from amulet.palette import BlockPalette as BlockPalette
from typing import Optional

log: Incomplete

class BaseBedrockTranslator(Translator):
    def _translator_key(self, version_number: VersionNumberAny) -> VersionIdentifierType: ...
    @staticmethod
    def _unpack_blocks(translation_manager: TranslationManager, version_identifier: VersionIdentifierType, chunk: Chunk, block_palette: AnyNDArray):
        """
        Unpacks an object array of block data into a numpy object array containing Block objects.
        :param translation_manager:
        :param version_identifier:
        :param chunk:
        :param block_palette:
        :type block_palette: numpy.ndarray[
            Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block],
                    Tuple[int, Block]
                ], ...
            ]
        ]
        :return:
        """
    def _blocks_entities_to_universal(self, game_version: VersionNumberTuple, translation_manager: TranslationManager, chunk: Chunk, get_chunk_callback: Optional[GetChunkCallback], full_translate: bool): ...
    def _blocks_entities_from_universal(self, max_world_version_number: VersionNumberAny, translation_manager: TranslationManager, chunk: Chunk, get_chunk_callback: Optional[GetChunkCallback], full_translate: bool):
        """
        Translate a universal chunk into the interface-specific format.

        :param max_world_version_number: The version number (int or tuple) of the max world version
        :param translation_manager: TranslationManager used for the translation
        :param chunk: The chunk to translate.
        :param get_chunk_callback: function callback to get a chunk's data
        :param full_translate: if true do a full translate. If false just pack the block_palette (used in callback)
        :return: Chunk object in the interface-specific format and block_palette.
        """
