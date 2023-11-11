from PyMCTranslate import TranslationManager as TranslationManager, Version as Version
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, BlockNDArray as BlockNDArray, VersionIdentifierType as VersionIdentifierType
from amulet.api.wrapper import Translator as Translator
from amulet.block import Block as Block
from amulet.palette import BlockPalette as BlockPalette

water: Incomplete

class JavaBlockstateTranslator(Translator):
    def _translator_key(self, version_number: int) -> VersionIdentifierType: ...
    @staticmethod
    def is_valid(key): ...
    @staticmethod
    def _unpack_blocks(translation_manager: TranslationManager, version_identifier: VersionIdentifierType, chunk: Chunk, block_palette: AnyNDArray):
        """
        Unpack the version-specific block_palette into the stringified version where needed.

        :return: The block_palette converted to block objects.
        """
    def _pack_block_palette(self, version: Version, palette: BlockNDArray) -> AnyNDArray:
        """
        Translate the list of block objects into a version-specific block_palette.
        :return: The block_palette converted into version-specific blocks (ie id, data tuples for 1.12)
        """
export = JavaBlockstateTranslator
