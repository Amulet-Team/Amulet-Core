from PyMCTranslate import Version as Version
from amulet.api.data_types import AnyNDArray as AnyNDArray, BlockNDArray as BlockNDArray
from amulet.block import Block as Block
from amulet.level.translators.chunk.bedrock import BaseBedrockTranslator as BaseBedrockTranslator

class BedrockNumericalTranslator(BaseBedrockTranslator):
    @staticmethod
    def is_valid(key): ...
    def _pack_block_palette(self, version: Version, palette: BlockNDArray) -> AnyNDArray:
        """
        Packs a numpy array of Block objects into an object array containing version number, block ids and block data values.
        :param version:
        :param palette:
        :return: numpy.ndarray[Tuple[Tuple[Optional[VersionNumber], Tuple[int, int]]]]
        """
export = BedrockNumericalTranslator
