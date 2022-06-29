from typing import List, Union, Type, Dict
import numpy

from amulet_nbt import (
    IntTag,
    DoubleTag,
    StringTag,
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    LongArrayTag,
    NamedTag,
)

from amulet.api.block import Block
from amulet.api.entity import Entity
from amulet.api.block_entity import BlockEntity
from amulet.api.registry import BlockManager


def unpack_palette(raw_palette: ListTag) -> List[Block]:
    block_palette = []
    extra_block_map: Dict[int, ListTag[IntTag]] = {}
    for block_index, block_nbt in enumerate(raw_palette):
        block_nbt: CompoundTag
        block = Block(
            namespace=block_nbt.get_string("namespace").py_str,
            base_name=block_nbt.get_string("blockname").py_str,
            properties=block_nbt.get_compound("properties").py_dict,
        )

        if block_nbt.get_list("extra_blocks"):
            extra_block_map[block_index] = block_nbt.get_list("extra_blocks")

        block_palette.append(block)

    extra_blocks: ListTag[IntTag]
    for block_index, extra_blocks in extra_block_map.items():
        extra_block_objects = [block_palette[i.py_int] for i in extra_blocks]

        resulting_block = block_palette[block_index]
        for extra_block in extra_block_objects:
            resulting_block = resulting_block + extra_block

        block_palette[block_index] = resulting_block
    return block_palette


def parse_entities(entities: ListTag) -> List[Entity]:
    return [
        Entity(
            entity.get_string("namespace").py_str,
            entity.get_string("base_name").py_str,
            entity.get_double("x").py_float,
            entity.get_double("y").py_float,
            entity.get_double("z").py_float,
            NamedTag(entity.get_compound("nbt")),
        )
        for entity in entities
    ]


def parse_block_entities(block_entities: ListTag) -> List[BlockEntity]:
    return [
        BlockEntity(
            block_entity.get_string("namespace").py_str,
            block_entity.get_string("base_name").py_str,
            block_entity.get_int("x").py_int,
            block_entity.get_int("y").py_int,
            block_entity.get_int("z").py_int,
            NamedTag(block_entity.get_compound("nbt")),
        )
        for block_entity in block_entities
    ]


def generate_block_entry(block: Block, palette_len, extra_blocks) -> CompoundTag:
    return CompoundTag(
        {
            "namespace": StringTag(block.namespace),
            "blockname": StringTag(block.base_name),
            "properties": CompoundTag(block.properties),
            "extra_blocks": ListTag(
                [
                    IntTag(palette_len + extra_blocks.index(_extra_block))
                    for _extra_block in block.extra_blocks
                ]
            ),
        }
    )


def serialise_entities(entities: List[Entity]) -> ListTag:
    return ListTag(
        [
            CompoundTag(
                {
                    "namespace": StringTag(entity.namespace),
                    "base_name": StringTag(entity.base_name),
                    "x": DoubleTag(entity.x),
                    "y": DoubleTag(entity.y),
                    "z": DoubleTag(entity.z),
                    "nbt": entity.nbt.compound,
                }
            )
            for entity in entities
        ]
    )


def serialise_block_entities(
    block_entities: List[BlockEntity],
) -> ListTag:
    return ListTag(
        [
            CompoundTag(
                {
                    "namespace": StringTag(block_entity.namespace),
                    "base_name": StringTag(block_entity.base_name),
                    "x": IntTag(block_entity.x),
                    "y": IntTag(block_entity.y),
                    "z": IntTag(block_entity.z),
                    "nbt": block_entity.nbt.compound,
                }
            )
            for block_entity in block_entities
        ]
    )


def find_fitting_array_type(
    array: numpy.ndarray,
) -> Union[Type[IntArrayTag], Type[ByteArrayTag], Type[LongArrayTag]]:
    max_element = array.max(initial=0)

    if max_element <= 127:
        return ByteArrayTag
    elif max_element <= 2_147_483_647:
        return IntArrayTag
    else:
        return LongArrayTag


def pack_palette(palette: BlockManager) -> ListTag:
    block_palette_nbt = ListTag()
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
