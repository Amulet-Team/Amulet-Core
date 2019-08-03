from __future__ import annotations

from collections import defaultdict
from typing import List, Union

import numpy
from nbt import nbt

from amulet.api import nbt_template
from amulet.api.chunk import Chunk
from amulet.utils import world_utils
from amulet.world_loading.decoders.decoder import Decoder


class AnvilDecoder(Decoder):
    def __init__(self):
        self._entity_handlers = defaultdict(nbt_template.EntityHandler)

    @staticmethod
    def identify(key):
        if key[0] != "anvil":
            return False
        if key[1] > 1343:
            return False
        return True

    def decode(self, data: nbt.TAG_Compound) -> Chunk:
        cx = data["Level"]["xPos"]
        cz = data["Level"]["zPos"]
        blocks = self._translate_blocks(data["Level"]["Sections"])
        entities = self._translate_entities(data["Level"]["Entities"])
        tile_entities = None
        return Chunk(cx, cz, blocks, entities, tile_entities)

    def _translate_entities(
        self, entities: list
    ) -> List[nbt_template.NBTCompoundEntry]:
        entity_list = []
        for entity in entities:
            entity = nbt_template.create_entry_from_nbt(entity)
            entity = self._entity_handlers[entity["id"].value].load_entity(entity)
            entity_list.append(entity)

        return entity_list

    def _translate_blocks(
        self, chunk_sections
    ) -> Union[numpy.ndarray, NotImplementedError]:
        if not chunk_sections:
            return NotImplementedError(
                "We don't support reading chunks that never been edited in Minecraft before"
            )

        blocks = numpy.zeros((256, 16, 16), dtype=int)
        block_data = numpy.zeros((256, 16, 16), dtype=numpy.uint8)
        for section in chunk_sections:
            lower = section["Y"].value << 4
            upper = (section["Y"].value + 1) << 4

            section_blocks = numpy.frombuffer(
                section["Blocks"].value, dtype=numpy.uint8
            )
            section_data = numpy.frombuffer(section["Data"].value, dtype=numpy.uint8)
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks.astype(numpy.uint16, copy=False)

            section_data = section_data.reshape(
                (16, 16, 8)
            )  # The Byte array is actually just Nibbles, so the size is off

            section_data = world_utils.from_nibble_array(section_data)

            if "Add" in section:
                add_blocks = numpy.frombuffer(section["Add"].value, dtype=numpy.uint8)
                add_blocks = add_blocks.reshape((16, 16, 8))
                add_blocks = world_utils.from_nibble_array(add_blocks)

                section_blocks |= add_blocks.astype(numpy.uint16) << 8

            blocks[lower:upper, :, :] = section_blocks
            block_data[lower:upper, :, :] = section_data

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)
        block_data = numpy.swapaxes(block_data.swapaxes(0, 1), 0, 2)

        return numpy.array((blocks, block_data)).T


DECODER_CLASS = AnvilDecoder
