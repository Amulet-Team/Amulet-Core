from __future__ import annotations

from typing import Dict, Iterable, List, Tuple, overload, Generator

from amulet.api.data_types import Int
from amulet.api.block import Block
from .base_registry import BaseRegistry


class BlockManager(BaseRegistry):
    """
    Class to handle the mappings between Block objects and their index-based internal IDs
    """

    def __init__(self, blocks: Iterable[Block] = ()):
        """
        Creates a new BlockManager object
        """
        self._index_to_block: List[Block] = []
        self._block_to_index_map: Dict[Block, int] = {}

        for block in blocks:
            assert isinstance(block, Block), "BlockManager only takes Block objects."
            if block not in self._block_to_index_map:
                self._block_to_index_map[block] = len(self._block_to_index_map)
            self._index_to_block.append(block)

    def __len__(self):
        return len(self._index_to_block)

    def __contains__(self, item: Block) -> bool:
        return item in self._block_to_index_map

    def __iter__(self):
        yield from self._index_to_block

    def blocks(self) -> Tuple[Block]:
        return tuple(self._index_to_block)

    def values(self) -> Tuple[Block]:
        return self.blocks()

    def items(self) -> Generator[Tuple[int, Block], None, None]:
        yield from enumerate(self._index_to_block)

    @overload
    def __getitem__(self, item: Block) -> int:
        ...

    @overload
    def __getitem__(self, item: Int) -> Block:
        ...

    def __getitem__(self, item):
        """
        If a Block object is passed to this function, it will return the internal ID/index of the blockstate.
        If an int is given, this method will return the Block object at that specified index.

        :param item: The Block object or int to get the mapping data of
        :return: An int if a Block object was supplied, a Block object if an int was supplied
        """
        try:
            if isinstance(item, Block):
                return self._block_to_index_map[item]

            return self._index_to_block[item]
        except (KeyError, IndexError):
            raise KeyError(
                f"There is no {item} in the BlockManager. "
                f"You might want to use the `get_add_block` function for your blocks before accessing them."
            )

    def get_add_block(self, block: Block) -> int:
        """
        Adds a Block object to the internal Block object/ID mappings. If the Block already exists in the mappings,
        then the existing ID is returned

        :param block: The Block to add to the manager
        :return: The internal ID of the Block
        """
        assert isinstance(block, Block), "BlockManager only takes Block objects."
        if block in self._block_to_index_map:
            return self._block_to_index_map[block]

        self._block_to_index_map[block] = i = len(self._block_to_index_map)
        self._index_to_block.append(block)

        return i

    def register(self, block: Block) -> int:
        return self.get_add_block(block)
