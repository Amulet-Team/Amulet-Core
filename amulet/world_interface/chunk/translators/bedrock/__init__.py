from __future__ import annotations

import numpy

from typing import Tuple, Callable, Union, Optional, TYPE_CHECKING

import amulet_nbt

from amulet import log
from amulet.api.block import Block
from amulet.api.data_types import BlockNDArray, AnyNDArray
from amulet.api.entity import Entity
from amulet.api.wrapper.chunk.translator import Translator
from amulet.api.data_types import GetBlockCallback, TranslateBlockCallbackReturn, TranslateEntityCallbackReturn, VersionNumberTuple, GetChunkCallback


if TYPE_CHECKING:
    from PyMCTranslate import Version, TranslationManager
    from amulet.api.block_entity import BlockEntity
    from amulet.api.chunk import Chunk


class BaseBedrockTranslator(Translator):
    def _translator_key(
        self, version_number: Union[int, VersionNumberTuple]
    ) -> Tuple[str, Union[int, VersionNumberTuple]]:
        return "bedrock", version_number

    def _unpack_palette(self, version: Version, palette: AnyNDArray) -> BlockNDArray:
        """
        Unpacks an object array of block data into a numpy object array containing Block objects.
        :param version:
        :param palette:
        :type palette: numpy.ndarray[
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
        palette_ = numpy.empty(len(palette), dtype=object)
        for palette_index, entry in enumerate(palette):
            entry: Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block],
                    Tuple[int, Block],
                ],
                ...,
            ]
            block = None
            for version_number, b in entry:
                version_number: Optional[int]
                if isinstance(b, tuple):
                    b = version.ints_to_block(*b)
                elif isinstance(b, Block):
                    if version_number is not None:
                        properties = b.properties
                        properties["__version__"] = amulet_nbt.TAG_Int(version_number)
                        b = Block(b.namespace, b.base_name, properties, b.extra_blocks)
                else:
                    raise Exception(f'Unsupported type {b}')
                if block is None:
                    block = b
                else:
                    block += b
            if block is None:
                raise Exception(f'Empty tuple')

            palette_[palette_index] = block
        return palette_

    def to_universal(
        self,
        game_version: VersionNumberTuple,
        translation_manager: 'TranslationManager',
        chunk: 'Chunk',
        palette: numpy.ndarray,
        get_chunk_callback: Union[
            Callable[[int, int], Tuple['Chunk', numpy.ndarray]], None
        ],
        full_translate: bool,
    ) -> Tuple['Chunk', numpy.ndarray]:
        # Bedrock does versioning by block rather than by chunk.
        # As such we can't just pass in a single translator.
        # It needs to be done dynamically.
        versions = {}

        def translate_block(
            input_object: Block,
            get_block_callback: Optional[GetBlockCallback],
        ) -> TranslateBlockCallbackReturn:
            final_block = None
            final_block_entity = None
            final_entities = []
            final_extra = False

            for depth, block in enumerate(input_object.block_tuple):
                if "__version__" in block.properties:
                    game_version_: int = block.properties["__version__"].value
                else:
                    if "block_data" in block.properties:
                        # if block_data is in properties cap out at 1.12.x
                        game_version_: VersionNumberTuple = min(game_version, (1, 12, 999))
                    else:
                        game_version_: VersionNumberTuple = game_version
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

        # TODO: split this into pack and translate stages
        chunk.biomes = self._biomes_to_universal(version, chunk.biomes)

        # TODO: move this into the packing stage
        if version.block_entity_map is not None:
            for block_entity in chunk.block_entities:
                block_entity: 'BlockEntity'
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

    def from_universal(
        self,
        max_world_version_number: Union[int, Tuple[int, int, int]],
        translation_manager: 'TranslationManager',
        chunk: Chunk,
        palette: BlockNDArray,
        get_chunk_callback: Optional[GetChunkCallback],
        full_translate: bool,
    ) -> Tuple[Chunk, BlockNDArray]:
        """
        Translate a universal chunk into the interface-specific format.

        :param max_world_version_number: The version number (int or tuple) of the max world version
        :param translation_manager: TranslationManager used for the translation
        :param chunk: The chunk to translate.
        :param palette: The palette that the chunk's indices correspond to.
        :param get_chunk_callback: function callback to get a chunk's data
        :param full_translate: if true do a full translate. If false just pack the palette (used in callback)
        :return: Chunk object in the interface-specific format and palette.
        """
        version = translation_manager.get_version(
            *self._translator_key(max_world_version_number)
        )

        # TODO: perhaps find a way so this code isn't duplicated in three places
        def translate_block(
            input_object: Block,
            get_block_callback: Optional[GetBlockCallback],
        ) -> TranslateBlockCallbackReturn:
            final_block = None
            final_block_entity = None
            final_entities = []
            final_extra = False

            for depth, block in enumerate(input_object.block_tuple):
                (
                    output_object,
                    output_block_entity,
                    extra,
                ) = version.block.from_universal(block, get_block_callback)

                if isinstance(output_object, Block):
                    if __debug__ and output_object.namespace.startswith(
                        "universal"
                    ):
                        log.debug(
                            f"Error translating {input_object.blockstate} from universal. Got {output_object.blockstate}"
                        )
                    if version.data_version > 0:
                        properties = output_object.properties
                        properties["__version__"] = amulet_nbt.TAG_Int(version.data_version)
                        output_object = Block(output_object.namespace, output_object.base_name, properties, output_object.extra_blocks)
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

        chunk, palette = self._translate(
            chunk, palette, get_chunk_callback, translate_block, translate_entity, full_translate
        )

        # TODO: split this into pack and translate stages
        chunk.biomes = self._biomes_from_universal(version, chunk.biomes)

        # TODO: move this into the packing stage
        if version.block_entity_map is not None:
            for block_entity in chunk.block_entities:
                block_entity: BlockEntity
                if block_entity.namespaced_name in version.block_entity_map_inverse:
                    block_entity.namespaced_name = version.block_entity_map_inverse[
                        block_entity.namespaced_name
                    ]
                else:
                    log.debug(
                        f"Could not find pretty name for block entity {block_entity.namespaced_name}"
                    )
        return chunk, palette
