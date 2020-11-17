from typing import TYPE_CHECKING, Any, Tuple, Union
import numpy

from amulet.api.wrapper import Interface
from .schematic import SchematicChunk
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionBox
from amulet.world_interface.chunk import translators
from amulet.api.data_types import AnyNDArray

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
        self, cx: int, cz: int, section: SchematicChunk
    ) -> Tuple["Chunk", AnyNDArray]:
        chunk = Chunk(cx, cz)
        block_palette, blocks = numpy.unique(
            (section.blocks << 4) + (section.data & 0xF), return_inverse=True
        )
        blocks = blocks.reshape(section.blocks.shape)
        palette = numpy.empty(len(block_palette) + 1, dtype=numpy.object)
        palette[0] = (0, 0)
        for index, block_num in enumerate(block_palette):
            palette[index + 1] = (block_num >> 4, block_num & 0xF)

        box = section.selection.create_moved_box((cx * 16, 0, cz * 16), subtract=True)
        chunk.blocks[box.slice] = blocks + 1
        for b in section.block_entities:
            b = self._decode_block_entity(
                b, self._block_entity_id_type, self._block_entity_coord_type
            )
            if b is not None:
                chunk.block_entities.insert(b)
        for b in section.entities:
            b = self._decode_entity(
                b, self._block_entity_id_type, self._block_entity_coord_type
            )
            if b is not None:
                chunk.entities.append(b)

        return chunk, palette

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        box: SelectionBox = None,
    ) -> SchematicChunk:
        entities = []
        for e in chunk.entities:
            if e.location in box:
                entities.append(
                    self._encode_entity(
                        e, self._entity_id_type, self._entity_coord_type
                    ).value
                )
        block_entities = []
        for e in chunk.block_entities:
            if e.location in box:
                block_entities.append(
                    self._encode_block_entity(
                        e, self._block_entity_id_type, self._block_entity_coord_type
                    ).value
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
        max_world_version: Tuple[str, Tuple[int, int, int]],
        data: Any = None,
        translation_manager: "TranslationManager" = None,
    ) -> Tuple["Translator", Union[int, Tuple[int, int, int]]]:
        platform, version_number = max_world_version
        if platform == "java":
            version = translation_manager.get_version(platform, version_number)
            version_number = version.data_version
        return translators.loader.get((platform, version_number)), version_number


class JavaSchematicInterface(SchematicInterface):
    _entity_id_type = "namespace-str-id"
    _entity_coord_type = "Pos-list-double"
    _block_entity_id_type = "namespace-str-id"
    _block_entity_coord_type = "xyz-int"


class BedrockSchematicInerface(SchematicInterface):
    _entity_id_type = "namespace-str-identifier"
    _entity_coord_type = "Pos-list-float"
    _block_entity_id_type = "str-id"
    _block_entity_coord_type = "xyz-int"
