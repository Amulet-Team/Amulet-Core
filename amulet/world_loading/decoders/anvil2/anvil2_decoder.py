from __future__ import annotations

from collections import defaultdict
from typing import List, Union, Tuple

import numpy
from nbt import nbt

from amulet.api import nbt_template
from amulet.api.block import Block
from amulet.api.chunk import Chunk
from amulet.world_loading.decoders.decoder import Decoder
from amulet.utils.world_utils import get_smallest_dtype


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

    def decode(self, data: nbt.TAG_Compound) -> Tuple[Chunk, numpy.ndarray]:
        cx = data["Level"]["xPos"]
        cz = data["Level"]["zPos"]
        blocks, palette = self._decode_blocks(data["Level"]["Sections"])
        entities = self._decode_entities(data["Level"]["Entities"])
        tile_entities = None
        return Chunk(cx, cz, blocks, entities, tile_entities), palette

    def _decode_blocks(
        self, chunk_sections
    ) -> Union[numpy.ndarray, NotImplementedError]:
        if not chunk_sections:
            return NotImplementedError(
                "We don't support reading chunks that never been edited in Minecraft before"
            )

        blocks = numpy.zeros((256, 16, 16), dtype=int)
        palette = [Block(namespace="minecraft", base_name="air")]

        for section in chunk_sections:
            if "Palette" not in section:  # 1.14 makes palette/blocks optional.
                continue
            height = section["Y"].value << 4

            blocks[height : height + 16, :, :] = _decode_long_array(
                section["BlockStates"].value, 4096
            ).reshape((16, 16, 16)) + len(palette)

            palette += self._read_palette(section["Palette"])

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)
        palette, inverse = numpy.unique(palette, return_inverse=True)
        blocks = inverse[blocks]

        return blocks.astype(f"uint{get_smallest_dtype(blocks)}"), palette

    def _decode_entities(self, entities: list) -> List[nbt_template.NBTCompoundEntry]:
        entity_list = []
        for entity in entities:
            entity = nbt_template.create_entry_from_nbt(entity)
            entity = self._entity_handlers[entity["id"].value].load_entity(entity)
            entity_list.append(entity)

        return entity_list

    def _read_palette(self, palette: nbt.TAG_List) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry["Name"].value.split(":", 1)
            properties = entry.get("Properties", {})
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    def get_translator(self, data: nbt.TAG_Compound) -> Tuple:
        return ("anvil", data["DataVersion"].value)


DECODER_CLASS = Anvil2Decoder
