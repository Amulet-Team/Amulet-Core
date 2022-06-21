from typing import List, Union, Type
import numpy

from amulet_nbt import IntTag, DoubleTag, StringTag, ListTag, CompoundTag, ByteArrayTag, IntArrayTag, LongArrayTag, NamedTag

from amulet.api.block import Block
from amulet.api.entity import Entity
from amulet.api.block_entity import BlockEntity
from amulet.api.registry import BlockManager


def unpack_palette(raw_palette: ListTag) -> List[Block]:
    block_palette = []
    extra_block_map = {}
    for block_index, block_nbt in enumerate(raw_palette):
        block_nbt: CompoundTag
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


def parse_entities(entities: ListTag) -> List[Entity]:
    return [
        Entity(
            entity["namespace"].value,
            entity["base_name"].value,
            entity["x"].value,
            entity["y"].value,
            entity["z"].value,
            NamedTag(entity["nbt"]),
        )
        for entity in entities
    ]


def parse_block_entities(block_entities: ListTag) -> List[BlockEntity]:
    return [
        BlockEntity(
            block_entity["namespace"].value,
            block_entity["base_name"].value,
            block_entity["x"].value,
            block_entity["y"].value,
            block_entity["z"].value,
            NamedTag(block_entity["nbt"]),
        )
        for block_entity in block_entities
    ]


def generate_block_entry(
    block: Block, palette_len, extra_blocks
) -> CompoundTag:
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
                    "nbt": entity.nbt.value,
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
                    "nbt": block_entity.nbt.value,
                }
            )
            for block_entity in block_entities
        ]
    )


def find_fitting_array_type(
    array: numpy.ndarray,
) -> Union[
    Type[IntArrayTag],
    Type[ByteArrayTag],
    Type[LongArrayTag],
]:
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
