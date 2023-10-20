from __future__ import annotations
from typing import Union, Iterable
from threading import Lock

from amulet.block import Block


class BlockPalette:
    """
    Class to handle the mappings between Block objects and their index-based internal IDs
    """

    def __init__(self, blocks: Iterable[Block] = ()):
        """
        Creates a new BlockManager object
        """
        self._lock = Lock()
        self._index_to_block: list[Block] = []
        self._block_to_index: dict[Block, int] = {}

        for block in blocks:
            self.block_to_index(block)

    def __len__(self):
        """
        The number of blocks in the registry.

        >>> block_palette: BlockPalette
        >>> len(block_palette)
        10
        """
        return len(self._index_to_block)

    def __contains__(self, item: Union[int, Block]) -> bool:
        """
        Is the given :class:`Block` already in the registry.

        >>> block_palette: BlockPalette
        >>> block: Block
        >>> block in block_palette
        True
        >>> 7 in block_palette
        True

        :param item: The block or index to check.
        """
        if isinstance(item, int):
            return item < len(self._index_to_block)
        elif isinstance(item, Block):
            return item in self._block_to_index
        return False

    def __iter__(self):
        """
        Iterate through all blocks in the registry.

        >>> block_palette: BlockPalette
        >>> for block in block_palette:
        >>>     ...
        """
        yield from self._index_to_block

    def index_to_block(self, index: int) -> Block:
        """
        Get the block at the specified palette index.
        :param index: The index to get
        :return: The block at that index
        :raises KeyError if there is no block at that index.
        """
        return self._index_to_block[index]

    def block_to_index(self, block: Block) -> int:
        """
        Get the index of the block in the palette.
        If it is not in the palette already it will be added first.
        :param block: The block to get the index of.
        :return: The index of the block in the palette.
        """
        if not isinstance(block, Block):
            raise TypeError(repr(block))
        if block not in self._block_to_index:
            with self._lock:
                if block not in self._block_to_index:
                    self._index_to_block.append(block)
                    self._block_to_index[block] = len(self._index_to_block) - 1
        return self._block_to_index[block]
