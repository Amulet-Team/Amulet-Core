from __future__ import annotations

import numpy

from typing import Tuple, Callable, Union, List, Optional

from amulet import log
from amulet.api.chunk import Chunk
from amulet.api.block import Block
from amulet.api.block_entity import BlockEntity
from amulet.api.entity import Entity
from amulet.world_interface.chunk.translators import Translator, TranslateBlockCallbackReturn, TranslateEntityCallbackReturn, VersionNumberType, BedrockBlockType
import PyMCTranslate
from PyMCTranslate.py3.translation_manager import Version

from .. import GetBlockCallback


class BaseBedrockTranslator(Translator):
    def _translator_key(
        self, version_number: VersionNumberType
    ) -> Tuple[str, VersionNumberType]:
        return "bedrock", version_number

    def _unpack_palette(self, version: Version, palette: numpy.ndarray):
        """
        Unpacks an object array of block data into a numpy object array containing Block objects.
        :param version:
        :param palette:
        :type palette: numpy.ndarray[
            Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block],
                    Tuple[Tuple[int, int, int, int], Block]
                ], ...
            ]
        ]
        :return:
        """
        palette_ = numpy.empty(len(palette), dtype=object)
        for palette_index, entry in enumerate(palette):
            entry: Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block],
                    Tuple[Tuple[int, int, int, int], Block],
                ],
                ...,
            ]
            palette_[palette_index] = tuple(
                (block[0], version.ints_to_block(*block[1]))
                if isinstance(block[1], tuple)
                else block
                for block in entry
            )
        return palette_

    def to_universal(
        self,
        game_version: VersionNumberType,
        translation_manager: PyMCTranslate.TranslationManager,
        chunk: Chunk,
        palette: numpy.ndarray,
        get_chunk_callback: Union[
            Callable[[int, int], Tuple[Chunk, numpy.ndarray]], None
        ],
        full_translate: bool,
    ) -> Tuple[Chunk, numpy.ndarray]:
        # Bedrock does versioning by block rather than by chunk.
        # As such we can't just pass in a single translator.
        # It needs to be done dynamically.
        versions = {}

        def translate_block(
            input_object: BedrockBlockType,
            get_block_callback: Optional[GetBlockCallback],
        ) -> TranslateBlockCallbackReturn:
            final_block = None
            final_block_entity = None
            final_entities = []
            final_extra = False

            for depth, block in enumerate(input_object):
                game_version_, block = block
                if game_version_ is None:
                    if "block_data" in block.properties:
                        # if block_data is in properties cap out at 1.12.x
                        game_version_ = min(game_version, (1, 12, 999))
                    else:
                        game_version_ = game_version
                version_key = self._translator_key(game_version_)
                if version_key not in versions:
                    versions[version_key] = translation_manager.get_version(
                        *version_key
                    ).block.to_universal
                output_object, output_block_entity, extra = versions[version_key](
                    block, get_block_callback
                )

                if isinstance(output_object, Block):
                    if not output_object.namespace.startswith("universal"):
                        log.debug(
                            f"Error translating {block.blockstate} to universal. Got {output_object.blockstate}"
                        )
                    if final_block is None:
                        final_block = output_object
                    else:
                        final_block += output_object
                    if depth == 0:
                        final_block_entity = output_block_entity

                elif isinstance(output_object, Entity):
                    final_entities.append(output_object)
                    # TODO: offset entity coords

                final_extra |= extra

            return final_block, final_block_entity, final_entities, final_extra

        def translate_entity(
            input_object: Entity
        ) -> TranslateEntityCallbackReturn:
            final_block = None
            final_block_entity = None
            final_entities = []
            # TODO
            return final_block, final_block_entity, final_entities

        version = translation_manager.get_version(*self._translator_key(game_version))
        palette = self._unpack_palette(version, palette)
        chunk.biomes = self._biomes_to_universal(version, chunk.biomes)
        if version.block_entity_map is not None:
            for block_entity in chunk.block_entities:
                block_entity: BlockEntity
                if (
                    block_entity.namespace is None
                    and block_entity.base_name in version.block_entity_map
                ):
                    block_entity.namespaced_name = version.block_entity_map[
                        block_entity.base_name
                    ]
                else:
                    log.debug(
                        f"Could not find pretty name for block entity {block_entity.namespaced_name}"
                    )

        return self._translate(
            chunk, palette, get_chunk_callback, translate_block, translate_entity, full_translate
        )
