from typing import TYPE_CHECKING, Any, Tuple
import numpy

from amulet.api.wrapper import Interface, EntityIDType, EntityCoordType
from .chunk import SchematicChunk
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionBox
from amulet.level.loader import Translators
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    VersionIdentifierType,
    PlatformType,
    VersionNumberTuple,
)

from amulet_nbt import NamedTag

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from PyMCTranslate import TranslationManager


class SchematicInterface(Interface):
    _entity_id_type = None
    _entity_coord_type = None
    _block_entity_id_type = None
    _block_entity_coord_type = None

    def is_valid(self, key: Tuple) -> bool:
        return True

    def decode(
        self, cx: int, cz: int, data: SchematicChunk
    ) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: Raw chunk data provided by the format.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        chunk = Chunk(cx, cz)
        block_palette, blocks = numpy.unique(
            (data.blocks << 4) + (data.data & 0xF), return_inverse=True
        )
        blocks = blocks.reshape(data.blocks.shape)
        palette = numpy.empty(len(block_palette) + 1, dtype=object)
        palette[0] = (0, 0)
        for index, block_num in enumerate(block_palette):
            palette[index + 1] = (block_num >> 4, block_num & 0xF)

        box = data.selection.create_moved_box((cx * 16, 0, cz * 16), subtract=True)
        chunk.blocks[box.slice] = blocks + 1
        for tag in data.block_entities:
            block_entity = self._decode_block_entity(
                NamedTag(tag), self._block_entity_id_type, self._block_entity_coord_type
            )
            if block_entity is not None:
                chunk.block_entities.insert(block_entity)
        for tag in data.entities:
            entity = self._decode_entity(
                NamedTag(tag), self._block_entity_id_type, self._block_entity_coord_type
            )
            if entity is not None:
                chunk.entities.append(entity)

        return chunk, palette

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: VersionIdentifierType,
        box: SelectionBox,
    ) -> SchematicChunk:
        """
        Take a version-specific chunk and encode it to raw data for the format to store.
        :param chunk: The already translated version-specfic chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param box: The volume of the chunk to pack.
        :return: Raw data to be stored by the Format.
        """
        entities = []
        for entity in chunk.entities:
            if entity.location in box:
                entities.append(
                    self._encode_entity(
                        entity, self._entity_id_type, self._entity_coord_type
                    ).compound
                )
        block_entities = []
        for block_entity in chunk.block_entities:
            if block_entity.location in box:
                block_entities.append(
                    self._encode_block_entity(
                        block_entity,
                        self._block_entity_id_type,
                        self._block_entity_coord_type,
                    ).compound
                )

        slices = box.create_moved_box(
            (chunk.cx * 16, 0, chunk.cz * 16), subtract=True
        ).slice
        blocks_merged = palette[chunk.blocks[slices]]

        return SchematicChunk(
            box,
            blocks_merged[:, :, :, 0].astype(numpy.uint16),
            blocks_merged[:, :, :, 1].astype(numpy.uint8),
            block_entities,
            entities,
        )

    def get_translator(
        self,
        max_world_version: Tuple[PlatformType, VersionNumberTuple],
        data: Any = None,
        translation_manager: "TranslationManager" = None,
    ) -> Tuple["Translator", VersionNumberAny]:
        platform, version_number = max_world_version
        if platform == "java":
            version = translation_manager.get_version(platform, version_number)
            version_number = version.data_version
        return Translators.get((platform, version_number)), version_number


class JavaSchematicInterface(SchematicInterface):
    _entity_id_type = EntityIDType.namespace_str_id
    _entity_coord_type = EntityCoordType.Pos_list_double
    _block_entity_id_type = EntityIDType.namespace_str_id
    _block_entity_coord_type = EntityCoordType.xyz_int


class BedrockSchematicInterface(SchematicInterface):
    _entity_id_type = EntityIDType.namespace_str_identifier
    _entity_coord_type = EntityCoordType.Pos_list_float
    _block_entity_id_type = EntityIDType.str_id
    _block_entity_coord_type = EntityCoordType.xyz_int
