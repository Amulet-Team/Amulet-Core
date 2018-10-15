from __future__ import annotations

import re
from typing import Dict, Iterable, List, Tuple, Union

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
        extra_blocks: Union[Block, Iterable[Block]] = None,
    ):
        self._namespace = namespace
        self._base_name = base_name
        self._properties = properties
        self._extra_blocks = ()
        if extra_blocks:
            if isinstance(extra_blocks, Block):
                extra_blocks = [extra_blocks]
            self._extra_blocks = tuple(extra_blocks)
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

    @property
    def extra_blocks(self) -> Union[Tuple, Tuple[Block]]:
        return self._extra_blocks

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

    def __repr__(self) -> str:
        return f"Block({', '.join([str(b) for b in (self, *self._extra_blocks)])})"

    def _compare_extra_blocks(self, other: Block) -> bool:
        if len(self._extra_blocks) != len(other._extra_blocks):
            return False

        if len(self._extra_blocks) == 0:
            return True

        for our_extra_block, their_extra_block in zip(
            self._extra_blocks, other._extra_blocks
        ):
            if our_extra_block != their_extra_block:
                return False

        return True

    def __eq__(self, other: Block) -> bool:
        if self.__class__ != other.__class__:
            return False

        return (
            self._namespace == other._namespace
            and self._base_name == other._base_name
            and self._properties == other._properties
            and self._compare_extra_blocks(other)
        )

    def __hash__(self):
        current_hash = hash(self._blockstate)

        if self._extra_blocks:
            current_hash = current_hash + hash(self._extra_blocks)

        return current_hash

    def __add__(self, other: Block) -> Block:
        if (
            len(other._extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(other._namespace, other._base_name, other._properties)

        other_extras = []
        for eb in other._extra_blocks:
            if (
                len(eb.extra_blocks) == 0
            ):  # Reduces the amount of extra objects/references created
                other_extras.append(eb)
            else:
                other_extras.append(Block(eb._namespace, eb._base_name, eb._properties))

        return Block(
            self._namespace,
            self._base_name,
            self._properties,
            [*self._extra_blocks, other_cpy, *other_extras],
        )

    def __sub__(self, other: Block) -> Block:
        if (
            len(other._extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(other._namespace, other._base_name, other._properties)

        other_extras = []
        for eb in other._extra_blocks:
            if len(eb.extra_blocks) == 0:
                other_extras.append(eb)
            else:
                other_extras.append(Block(eb._namespace, eb._base_name, eb._properties))

        # Sets are unordered, so a regular set subtraction doesn't always return the order we want (it sometimes will!)
        # So we loop through all of our extra blocks and only append those to the new_extras list if they aren't in
        # extra_blocks_to_remove
        new_extras = []
        extra_blocks_to_remove = (other_cpy, *other_extras)
        for eb in self._extra_blocks:
            if eb not in extra_blocks_to_remove:
                new_extras.append(eb)

        return Block(self._namespace, self._base_name, self._properties, new_extras)

    def __iadd__(self, other: Block) -> TypeError:
        raise TypeError("You cannot add an extra block to an already existing block")

    def __isub__(self, other: Block) -> TypeError:
        raise TypeError(
            "You cannot subtract an extra block to an already existing block"
        )


class BlockManager:
    def __init__(self):
        self._index_to_block: List[Block] = []
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

        if isinstance(item, Block) and item not in self._block_to_index_map:
            self._add_block(item)

        return self._block_to_index_map[item]

    def _add_block(self, block: Block) -> int:
        self._block_to_index_map[block] = i = len(self._block_to_index_map)
        self._index_to_block.append(block)

        return i

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

    eb = Block.get_from_blockstate("minecraft:stone")

    water = Block.get_from_blockstate("minecraft:water")
    eb2 = Block.get_from_blockstate("minecraft:dirt") + water

    eb3 = water + Block.get_from_blockstate("minecraft:dirt")
    print(f"eb2 == eb3: {eb2 == eb3}")
    print(f"hash(eb2) == hash(eb3): {hash(eb2) == hash(eb3)}")

    manager = BlockManager()
    start1 = time.time()
    i1 = manager["minecraft:air"]
    end1 = time.time()
    i2 = manager["minecraft:stone"]

    i4 = manager[eb2]

    start2 = time.time()
    i3 = manager["minecraft:air"]
    end2 = time.time()
    print(i1, i2, i3, i4)
    print(b == "minecraft:unknown")
    print(f"Creation: {end1 - start1}")
    print(f"__getitem__: {end2 - start2}")
    print(manager._block_to_index_map, "\n", manager._index_to_block)

    time.sleep(0.5)

    block = manager[4]
    i4 = manager[b]
