from __future__ import annotations

from collections.abc import Iterable

from amulet_nbt import CompoundTag, ListTag, StringTag

from amulet.api.block import Block

from .anvil_3463 import (
    Anvil3463Interface as ParentInterface,
)


class Anvil5006Interface(ParentInterface):
    @staticmethod
    def minor_is_valid(key: int):
        return 5006 <= key <= 5100

    @staticmethod
    def _decode_block_palette(palette: ListTag) -> list:
        blockstates = []
        for entry in palette:
            if isinstance(entry, CompoundTag):
                root = entry.get("", None)
                if root is not None:
                    entry = root
            if isinstance(entry, StringTag):
                namespace, base_name = entry.py_str.split(":", 1)
                properties = {}
            elif isinstance(entry, CompoundTag):
                namespace, base_name = entry.get_string("id").py_str.split(":", 1)
                properties = entry.get_compound("properties", CompoundTag({})).py_dict
            else:
                raise ValueError(f"Invalid block palette entry: {entry}")
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    @staticmethod
    def _encode_block_palette(blockstates: Iterable[Block]) -> ListTag:
        palette_list = []
        is_compound_list = False
        for block in blockstates:
            if block.properties:
                is_compound_list = True
                entry = CompoundTag()
                entry["id"] = StringTag(f"{block.namespace}:{block.base_name}")
                if block.properties:
                    string_properties = {
                        k: v
                        for k, v in block.properties.items()
                        if isinstance(v, StringTag)
                    }
                    if string_properties:
                        entry["properties"] = CompoundTag(string_properties)
                palette_list.append(entry)
            else:
                palette_list.append(StringTag(f"{block.namespace}:{block.base_name}"))
        if is_compound_list:
            palette_list = [
                CompoundTag({"": entry}) if isinstance(entry, StringTag) else entry
                for entry in palette_list
            ]
        return ListTag(palette_list)


export = Anvil5006Interface
