from __future__ import annotations

from typing import Tuple, Union, TYPE_CHECKING
import amulet_nbt

from amulet.api.chunk import Chunk
from amulet.api.wrapper import Translator
from amulet.api.block import Block, blockstate_to_block
from amulet.api.registry import BlockManager
from amulet.api.data_types import (
    VersionIdentifierType,
    AnyNDArray,
    BlockNDArray,
)

if TYPE_CHECKING:
    from PyMCTranslate import Version, TranslationManager

water = blockstate_to_block('minecraft:water[level="0"]')


class JavaBlockstateTranslator(Translator):
    def _translator_key(
        self, version_number: int
    ) -> Tuple[str, Union[int, Tuple[int, int, int]]]:
        return "java", version_number

    @staticmethod
    def is_valid(key):
        if key[0] != "java":
            return False
        if key[1] < 1444:
            return False
        return True

    @staticmethod
    def _unpack_blocks(
        translation_manager: "TranslationManager",
        version_identifier: VersionIdentifierType,
        chunk: Chunk,
        block_palette: AnyNDArray,
    ):
        """
        Unpack the version-specific block_palette into the stringified version where needed.

        :return: The block_palette converted to block objects.
        """
        version = translation_manager.get_version(*version_identifier)
        for index, block in enumerate(block_palette):
            block: Block
            if version.is_waterloggable(block.namespaced_name):
                properties = block.properties
                if "waterlogged" in properties:
                    waterlogged = properties["waterlogged"]
                    del properties["waterlogged"]
                    block = Block(
                        namespace=block.namespace,
                        base_name=block.base_name,
                        properties=properties,
                    )
                else:
                    waterlogged = amulet_nbt.TAG_String("false")

                if waterlogged == amulet_nbt.TAG_String("true"):
                    block_palette[index] = block + water
                else:
                    block_palette[index] = block
            elif version.block.is_waterloggable(block.namespaced_name, True):
                block_palette[index] = block + water

        chunk._block_palette = BlockManager(block_palette)

    def _pack_block_palette(
        self, version: "Version", palette: BlockNDArray
    ) -> AnyNDArray:
        """
        Translate the list of block objects into a version-specific block_palette.
        :return: The block_palette converted into version-specific blocks (ie id, data tuples for 1.12)
        """
        for index, block in enumerate(palette):
            block: Block
            if version.block.is_waterloggable(block.namespaced_name):
                properties = block.properties
                extra_blocks = block.extra_blocks
                if (
                    extra_blocks
                    and extra_blocks[0].namespaced_name == water.namespaced_name
                ):
                    properties["waterlogged"] = amulet_nbt.TAG_String("true")
                else:
                    properties["waterlogged"] = amulet_nbt.TAG_String("false")
                palette[index] = Block(
                    namespace=block.namespace,
                    base_name=block.base_name,
                    properties=properties,
                )
        return palette


TRANSLATOR_CLASS = JavaBlockstateTranslator
