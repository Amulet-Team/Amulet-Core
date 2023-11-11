from PyMCTranslate import TranslationManager as TranslationManager, Version as Version
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, BlockNDArray as BlockNDArray, VersionIdentifierType as VersionIdentifierType
from amulet.api.wrapper import Translator as Translator
from amulet.palette import BlockPalette as BlockPalette

class JavaNumericalTranslator(Translator):
    def _translator_key(self, version_number: int) -> VersionIdentifierType: ...
    @staticmethod
    def _unpack_blocks(translation_manager: TranslationManager, version_identifier: VersionIdentifierType, chunk: Chunk, block_palette: AnyNDArray):
        """
        Unpacks an int array of block ids and block data values [[1, 0], [2, 0]] into a numpy array of Block objects.
        :param translation_manager:
        :param version_identifier:
        :param chunk:
        :param block_palette:
        :return:
        """
    def _pack_block_palette(self, version: Version, palette: BlockNDArray) -> AnyNDArray:
        """
        Packs a numpy array of Block objects into an int array of block ids and block data values [[1, 0], [2, 0]].
        :param version:
        :param palette:
        :return:
        """
    @staticmethod
    def is_valid(key): ...
export = JavaNumericalTranslator
