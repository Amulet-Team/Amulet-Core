from typing import TYPE_CHECKING, Any, Tuple, Union
import numpy

from amulet.api.wrapper import Interface, EntityIDType, EntityCoordType
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionBox
from amulet.api.data_types import AnyNDArray
from amulet.level.loader import Translators
from amulet.api.block import Block
from .chunk import SpongeSchemChunk

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from PyMCTranslate import TranslationManager


class SpongeSchemInterface(Interface):
    _entity_id_type = EntityIDType.namespace_str_Id
    _entity_coord_type = EntityCoordType.Pos_list_double
    _block_entity_id_type = EntityIDType.namespace_str_Id
    _block_entity_coord_type = EntityCoordType.Pos_array_int

    def is_valid(self, key: Tuple) -> bool:
        return True

    def decode(
        self, cx: int, cz: int, section: SpongeSchemChunk
    ) -> Tuple["Chunk", AnyNDArray]:
        palette = numpy.empty(len(section.palette) + 1, dtype=numpy.object)
        palette[0] = Block(namespace="minecraft", base_name="air")
        palette[1:] = section.palette[:]

        chunk = Chunk(cx, cz)
        box = section.selection.create_moved_box((cx * 16, 0, cz * 16), subtract=True)
        chunk.blocks[box.slice] = section.blocks + 1
        for b in section.block_entities:
            b = self._decode_block_entity(
                b, self._block_entity_id_type, self._block_entity_coord_type
            )
            if b is not None:
                chunk.block_entities.insert(b)
        for e in section.entities:
            e = self._decode_entity(
                e, self._block_entity_id_type, self._block_entity_coord_type
            )
            if e is not None:
                chunk.entities.append(e)

        return chunk, palette

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        box: SelectionBox = None,
    ) -> SpongeSchemChunk:
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

        return SpongeSchemChunk(
            box,
            numpy.asarray(chunk.blocks[slices]),
            palette.copy(),
            block_entities,
            entities,
        )

    def get_translator(
        self,
        max_world_version: Tuple[str, int],
        data: Any = None,
        translation_manager: "TranslationManager" = None,
    ) -> Tuple["Translator", Union[int, Tuple[int, int, int]]]:
        platform, version_number = max_world_version
        if platform != "java":
            raise ValueError("Platform must be java")
        version = translation_manager.get_version(platform, version_number)
        version_number = version.data_version
        return Translators.get((platform, version_number)), version_number
