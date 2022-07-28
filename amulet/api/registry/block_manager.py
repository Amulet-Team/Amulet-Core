from __future__ import annotations
from typing import Dict, Iterable, List, Tuple, overload, Generator, Union
from numpy import integer

from amulet_nbt import ByteTag, IntTag, ShortTag, LongTag

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
        """
        The number of blocks in the registry.

        >>> len(level.block_palette)
        10
        """
        return len(self._index_to_block)

    def __contains__(self, item: Block) -> bool:
        """
        Is the given :class:`Block` already in the registry.

        >>> block in level.block_palette
        True
        >>> 7 in level.block_palette
        True

        :param item: The block or index to check.
        """
        if isinstance(item, int):
            return item < len(self._index_to_block)
        elif isinstance(item, Block):
            return item in self._block_to_index_map
        return False

    def __iter__(self):
        """
        Iterate through all blocks in the registry.

        >>> for block in level.block_palette:
        >>>     ...
        """
        yield from self._index_to_block

    @property
    def blocks(self) -> Tuple[Block, ...]:
        """
        The blocks in the registry as a tuple.
        """
        return tuple(self._index_to_block)

    def values(self) -> Tuple[Block, ...]:
        """
        The blocks in the registry as a tuple.
        """
        return self.blocks

    def items(self) -> Generator[Tuple[int, Block], None, None]:
        """
        A generator of the block indexes and the block objects.
        """
        yield from enumerate(self._index_to_block)

    @overload
    def __getitem__(self, item: Block) -> int:
        ...

    @overload
    def __getitem__(self, item: Int) -> Block:
        ...

    @overload
    def __getitem__(self, item: Iterable[Union[Int, Block]]) -> List[Union[Block, Int]]:
        ...

    def __getitem__(self, item):
        """
        If a Block object is passed to this function, it will return the internal ID/index of the blockstate.

        If an int is given, this method will return the Block object at that specified index.

        >>> level.block_palette[block]
        7
        >>> level.block_palette[7]
        block

        :param item: The Block object or int to get the mapping data of
        :return: An int if a Block object was supplied, a Block object if an int was supplied
        :raises KeyError if the requested item is not present.
        """
        try:
            return self._get_item(item)
        except (KeyError, IndexError):
            raise KeyError(
                f"There is no {item} in the BlockManager. "
                f"You might want to use the `get_add_block` function for your blocks before accessing them."
            )

    def _get_item(self, item):
        if isinstance(item, Block):
            return self._block_to_index_map[item]
        elif isinstance(item, (int, integer, ByteTag, ShortTag, IntTag, LongTag)):
            return self._index_to_block[int(item)]
        # if it isn't an Block or int assume an iterable of the above.
        return [self._get_item(i) for i in item]

    def get_add_block(self, block: Block) -> int:
        """
        Adds a Block object to the internal Block object/ID mappings.

        If the Block already exists in the mappings, the existing ID is returned.

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
        """
        An alias of :meth:`get_add_block`.

        Adds a Block object to the internal Block object/ID mappings.

        If the Block already exists in the mappings, the existing ID is returned.

        :param block: The Block to add to the manager
        :return: The internal ID of the Block
        """
        return self.get_add_block(block)
