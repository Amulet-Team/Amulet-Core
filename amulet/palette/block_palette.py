from __future__ import annotations
from typing import Union
from threading import Lock
from collections.abc import Sequence

from amulet.block import BlockStack
from amulet.version import VersionRange, VersionRangeContainer


class BlockPalette(VersionRangeContainer, Sequence[BlockStack]):
    """
    Class to handle the mappings between Block Stack objects and their index-based internal IDs
    """

    def __init__(self, version_range: VersionRange):
        """
        Creates a new BlockPalette object
        """
        super().__init__(version_range)
        self._lock = Lock()
        self._index_to_block: list[BlockStack] = []
        self._block_to_index: dict[BlockStack, int] = {}

    def __len__(self):
        """
        The number of block stacks in the palette.

        >>> block_palette: BlockPalette
        >>> len(block_palette)
        10
        """
        return len(self._index_to_block)

    def __getitem__(self, item):
        return self._index_to_block[item]

    def __contains__(self, item: Union[int, BlockStack]) -> bool:
        """
        Is the given :class:`BlockStack` already in the palette.

        >>> block_palette: BlockPalette
        >>> block_stack: BlockStack
        >>> block_stack in block_palette
        True
        >>> 7 in block_palette
        True

        :param item: The block stack or index to check.
        """
        if isinstance(item, int):
            return item < len(self._index_to_block)
        elif isinstance(item, BlockStack):
            return item in self._block_to_index
        return False

    def index_to_block_stack(self, index: int) -> BlockStack:
        """
        Get the block stack at the specified palette index.
        :param index: The index to get
        :return: The block stack at that index
        :raises KeyError if there is no block stack at that index.
        """
        return self._index_to_block[index]

    def block_stack_to_index(self, block_stack: BlockStack) -> int:
        """
        Get the index of the block stack in the palette.
        If it is not in the palette already it will be added first.
        :param block_stack: The block stack to get the index of.
        :return: The index of the block stack in the palette.
        """
        if not isinstance(block_stack, BlockStack):
            raise TypeError(repr(block_stack))
        if not all(block.version in self.version_range for block in block_stack):
            raise ValueError(
                f"BlockStack {block_stack} is incompatible with {self.version_range}"
            )
        if block_stack not in self._block_to_index:
            with self._lock:
                if block_stack not in self._block_to_index:
                    self._index_to_block.append(block_stack)
                    self._block_to_index[block_stack] = len(self._index_to_block) - 1
        return self._block_to_index[block_stack]
