from PyMCTranslate import Version as Version
from amulet.api.data_types import AnyNDArray as AnyNDArray, BlockNDArray as BlockNDArray
from amulet.block import Block as Block
from amulet.level.translators.chunk.bedrock import BaseBedrockTranslator as BaseBedrockTranslator

class BedrockNBTBlockstateTranslator(BaseBedrockTranslator):
    @staticmethod
    def is_valid(key): ...
    def _pack_block_palette(self, version: Version, palette: BlockNDArray) -> AnyNDArray:
        """
        Packs a numpy array of Block objects into an object array containing one more more pairs of version number and Block objects.
        :param version:
        :param palette:
        :return: numpy.ndarray[Tuple[Tuple[Optional[VersionNumber], Block], ...]]
        """
export = BedrockNBTBlockstateTranslator
