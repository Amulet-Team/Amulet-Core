from typing import List, Union, Type
import numpy

import amulet_nbt

from amulet.api.block import Block
from amulet.api.entity import Entity
from amulet.api.block_entity import BlockEntity
from amulet.api.registry import BlockManager


def unpack_palette(raw_palette: amulet_nbt.TAG_List) -> List[Block]:
    block_palette = []
    extra_block_map = {}
    for block_index, block_nbt in enumerate(raw_palette):
        block_nbt: amulet_nbt.TAG_Compound
        block_namespace = block_nbt["namespace"].value
        block_basename = block_nbt["blockname"].value
        block = Block(
            namespace=block_namespace,
            base_name=block_basename,
            properties=block_nbt["properties"].value,
        )

        if block_nbt["extra_blocks"].value:
            extra_block_map[block_index] = block_nbt["extra_blocks"].value

        block_palette.append(block)

    for block_index, extra_blocks in extra_block_map.items():
        extra_block_objects = [block_palette[i.value] for i in extra_blocks]

        resulting_block = block_palette[block_index]
        for extra_block in extra_block_objects:
            resulting_block = resulting_block + extra_block

        block_palette[block_index] = resulting_block
    return block_palette


def parse_entities(entities: amulet_nbt.TAG_List) -> List[Entity]:
    return [
        Entity(
            entity["namespace"].value,
            entity["base_name"].value,
            entity["x"].value,
            entity["y"].value,
            entity["z"].value,
            amulet_nbt.NBTFile(entity["nbt"]),
        )
        for entity in entities
    ]


def parse_block_entities(block_entities: amulet_nbt.TAG_List) -> List[BlockEntity]:
    return [
        BlockEntity(
            block_entity["namespace"].value,
            block_entity["base_name"].value,
            block_entity["x"].value,
            block_entity["y"].value,
            block_entity["z"].value,
            amulet_nbt.NBTFile(block_entity["nbt"]),
        )
        for block_entity in block_entities
    ]


def generate_block_entry(
    block: Block, palette_len, extra_blocks
) -> amulet_nbt.TAG_Compound:
    return amulet_nbt.TAG_Compound(
        {
            "namespace": amulet_nbt.TAG_String(block.namespace),
            "blockname": amulet_nbt.TAG_String(block.base_name),
            "properties": amulet_nbt.TAG_Compound(block.properties),
            "extra_blocks": amulet_nbt.TAG_List(
                [
                    amulet_nbt.TAG_Int(palette_len + extra_blocks.index(_extra_block))
                    for _extra_block in block.extra_blocks
                ]
            ),
        }
    )


def serialise_entities(entities: List[Entity]) -> amulet_nbt.TAG_List:
    return amulet_nbt.TAG_List(
        [
            amulet_nbt.TAG_Compound(
                {
                    "namespace": amulet_nbt.TAG_String(entity.namespace),
                    "base_name": amulet_nbt.TAG_String(entity.base_name),
                    "x": amulet_nbt.TAG_Double(entity.x),
                    "y": amulet_nbt.TAG_Double(entity.y),
                    "z": amulet_nbt.TAG_Double(entity.z),
                    "nbt": entity.nbt.value,
                }
            )
            for entity in entities
        ]
    )


def serialise_block_entities(
    block_entities: List[BlockEntity],
) -> amulet_nbt.TAG_List:
    return amulet_nbt.TAG_List(
        [
            amulet_nbt.TAG_Compound(
                {
                    "namespace": amulet_nbt.TAG_String(block_entity.namespace),
                    "base_name": amulet_nbt.TAG_String(block_entity.base_name),
                    "x": amulet_nbt.TAG_Int(block_entity.x),
                    "y": amulet_nbt.TAG_Int(block_entity.y),
                    "z": amulet_nbt.TAG_Int(block_entity.z),
                    "nbt": block_entity.nbt.value,
                }
            )
            for block_entity in block_entities
        ]
    )


def find_fitting_array_type(
    array: numpy.ndarray,
) -> Union[
    Type[amulet_nbt.TAG_Int_Array],
    Type[amulet_nbt.TAG_Byte_Array],
    Type[amulet_nbt.TAG_Long_Array],
]:
    max_element = array.max(initial=0)

    if max_element <= 127:
        return amulet_nbt.TAG_Byte_Array
    elif max_element <= 2_147_483_647:
        return amulet_nbt.TAG_Int_Array
    else:
        return amulet_nbt.TAG_Long_Array


def pack_palette(palette: BlockManager) -> amulet_nbt.TAG_List:
    block_palette_nbt = amulet_nbt.TAG_List()
    extra_blocks = set()

    for block in palette.blocks:
        if len(block.extra_blocks) > 0:
            extra_blocks.update(block.extra_blocks)

    extra_blocks = list(extra_blocks)

    palette_len = len(palette)
    for block_entry in palette.blocks:
        block_palette_nbt.append(
            generate_block_entry(block_entry, palette_len, extra_blocks)
        )

    for extra_block in extra_blocks:
        block_palette_nbt.append(
            generate_block_entry(extra_block, palette_len, extra_blocks)
        )
    return block_palette_nbt
