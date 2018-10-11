from __future__ import annotations

import re
from typing import Dict, Union

import time


class MalformedBlockstateException(Exception):
    pass


class Block:
    blockstate_regex = re.compile(
        r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_]+)(?P<properties>.*)\])?"
    )

    parameters_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_]+))")

    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: Dict[str, Union[str, bool, int]],
    ):
        self._namespace = namespace
        self._base_name = base_name
        self._properties = properties
        self._blockstate = self._gen_blockstate()

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def base_name(self) -> str:
        return self._base_name

    @property
    def properties(self) -> Dict[str, Union[str, bool, int]]:
        return self._properties

    @property
    def blockstate(self) -> str:
        return self._blockstate

    def _gen_blockstate(self) -> str:
        blockstate = f"{self._namespace}:{self._base_name}"
        if self._properties:
            props = [f"{key}={value}" for key, value in self._properties.items()]
            blockstate += f"[{','.join(props)}]"
        return blockstate

    @classmethod
    def get_from_blockstate(cls, blockstate: str) -> Block:
        match = Block.blockstate_regex.match(blockstate)
        namespace = match.group("namespace") or "minecraft"
        base_name = match.group("base_name")

        if match.group("property_name") is not None:
            properties = {match.group("property_name"): match.group("property_value")}
        else:
            properties = {}

        properties_string = match.group("properties")
        if properties_string is not None:
            properties_match = Block.parameters_regex.finditer(properties_string)
            for match in properties_match:
                properties[match.group("name")] = match.group("value")

        return cls(namespace, base_name, properties)

    def __str__(self) -> str:
        return self._blockstate

    def __repr__(self):
        return f"Block({self._namespace}, {self._base_name}, {self._properties})"

    def __eq__(self, other: Block) -> bool:
        if not isinstance(other, Block):
            return False

        return (
            self._namespace == other._namespace
            and self._base_name == other._base_name
            and self._properties == other._properties
        )

    def __hash__(self):
        return hash(self._blockstate)


class BlockManager:
    def __init__(self):
        self._index_to_block = []
        self._block_to_index_map: Dict[Block, int] = {}

    def __getitem__(self, item: Union[Block, str, int]) -> Union[Block, int]:
        """
        If a Block object or string is passed to this function, it'll return the internal ID/index of the
        blockstate. If an int is given, this method will return the Block object at that specified index.

        :param item:
        :return:
        """
        if isinstance(item, str):
            item = self.get_block(item)

        if isinstance(item, int):
            return self._index_to_block[item]

        return self._block_to_index_map[item]

    def get_block(self, block: str) -> Block:
        b = Block.get_from_blockstate(block)

        if b in self._block_to_index_map:
            i = self._block_to_index_map[b]
            del b
            return self._index_to_block[i]

        self._block_to_index_map[b] = len(self._block_to_index_map)
        self._index_to_block.append(b)

        return b


if __name__ == "__main__":
    b = Block.get_from_blockstate("minecraft:unknown")

    manager = BlockManager()
    start1 = time.time()
    i1 = manager["minecraft:air"]
    end1 = time.time()
    i2 = manager["minecraft:stone"]

    start2 = time.time()
    i3 = manager["minecraft:air"]
    end2 = time.time()
    print(i1, i2, i3)
    print(b == "minecraft:unknown")
    print(f"Creation: {end1 - start1}")
    print(f"__getitem__: {end2 - start2}")
    print(manager._block_to_index_map, "|", manager._index_to_block)

    time.sleep(0.5)

    block = manager[4]
    i4 = manager[b]
