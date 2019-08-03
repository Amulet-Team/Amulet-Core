from __future__ import annotations

from collections import defaultdict
from typing import List, Union

import numpy
from nbt import nbt

from amulet.api import nbt_template
from amulet.api.chunk import Chunk
from amulet.world_loading.decoders.decoder import Decoder

def properties_to_string(props: dict) -> str:
    """
    Converts a dictionary of blockstate properties to a string

    :param props: The dictionary of blockstate properties
    :return: The string version of the supplied blockstate properties
    """
    result = []
    for key, value in props.items():
        result.append("{}={}".format(key, value))
    return ",".join(result)

def _decode_long_array(long_array: array_like, size: int) -> numpy.ndarray:
    """
    Decode an long array (from BlockStates or Heightmaps)
    :param long_array: Encoded long array
    :size uint: The expected size of the returned array
    :return: Decoded array as numpy array
    """
    long_array = numpy.array(long_array, dtype=">q")
    bits_per_block = (len(long_array) * 64) // size
    binary_blocks = numpy.unpackbits(
        long_array[::-1].astype(">i8").view("uint8")
    ).reshape(-1, bits_per_block)
    return binary_blocks.dot(2 ** numpy.arange(binary_blocks.shape[1] - 1, -1, -1))[
        ::-1  # Undo the bit-shifting that Minecraft does with the palette indices
    ][:size]

class Anvil2Decoder(Decoder):
    def __init__(self):
        self._entity_handlers = defaultdict(nbt_template.EntityHandler)

    @staticmethod
    def identify(key):
        if key[0] != "anvil":
            return False
        if key[1] < 1444:
            return False
        return True

    def decode(self, data: nbt.TAG_Compound) -> Chunk:
        cx = data["Level"]["xPos"]
        cz = data["Level"]["zPos"]
        blocks = self._translate_blocks(data["Level"]["Sections"])
        entities = self._translate_entities(data["Level"]["Entities"])
        tile_entities = None
        return Chunk(cx, cz, blocks, entities, tile_entities)

    def _read_palette(self, palette: nbt.TAG_List) -> list:
        blockstates = []
        for entry in palette:
            name = entry["Name"].value
            properties = properties_to_string(entry.get("Properties", {}))
            if properties:
                blockstates.append(f"{name}[{properties}]")
            else:
                blockstates.append(name)
        return blockstates

    def _translate_entities(self, entities: list) -> List[nbt_template.NBTCompoundEntry]:
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

        blocks = numpy.full((256, 16, 16), "minecraft:air", dtype="object")

        for section in chunk_sections:
            lower = section["Y"].value << 4
            upper = (section["Y"].value + 1) << 4

            palette = self._read_palette(section["Palette"])

            _blocks = numpy.asarray(palette, dtype="object")[
                _decode_long_array(section["BlockStates"].value, 4096)
            ]  # Mask the decoded long array with the entries from the palette

            blocks[lower:upper, :, :] = _blocks.reshape((16, 16, 16))

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)

        return blocks

DECODER_CLASS = Anvil2Decoder
