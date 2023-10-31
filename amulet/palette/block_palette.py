from __future__ import annotations
from typing import Union
from threading import Lock
from collections.abc import Sequence

from amulet.block import BlockStack, Block
from amulet.game_version import GameVersionRange


class BlockPalette(Sequence[BlockStack]):
    """
    Class to handle the mappings between Block Stack objects and their index-based internal IDs
    """

    def __init__(self, version_range: GameVersionRange):
        """
        Creates a new BlockManager object
        """
        self._lock = Lock()
        self._index_to_block: list[BlockStack] = []
        self._block_to_index: dict[BlockStack, int] = {}
        self._version_range = version_range

    def __len__(self):
        """
        The number of blocks in the registry.

        >>> block_palette: BlockPalette
        >>> len(block_palette)
        10
        """
        return len(self._index_to_block)

    def __getitem__(self, item):
        return self._index_to_block[item]

    def __contains__(self, item: Union[int, BlockStack]) -> bool:
        """
        Is the given :class:`Block` already in the registry.

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
            return self.fix_block(item) in self._block_to_index
        return False

    def index_to_block(self, index: int) -> BlockStack:
        """
        Get the block at the specified palette index.
        :param index: The index to get
        :return: The block at that index
        :raises KeyError if there is no block at that index.
        """
        return self._index_to_block[index]

    def block_to_index(self, block: BlockStack) -> int:
        """
        Get the index of the block in the palette.
        If it is not in the palette already it will be added first.
        :param block: The block to get the index of.
        :return: The index of the block in the palette.
        """
        if not isinstance(block, BlockStack):
            raise TypeError(repr(block))
        block = self.fix_block(block)
        if block not in self._block_to_index:
            with self._lock:
                if block not in self._block_to_index:
                    self._index_to_block.append(block)
                    self._block_to_index[block] = len(self._index_to_block) - 1
        return self._block_to_index[block]

    def fix_block(self, block_stack: BlockStack) -> BlockStack:
        """If a version has not been set for a block this sets the maximum version this palette supports."""
        blocks = []
        for block in block_stack:
            if block.version is None:
                blocks.append(
                    Block(
                        block.namespace,
                        block.base_name,
                        block.properties,
                        self._version_range.max,
                    )
                )
            elif block.version in self._version_range:
                blocks.append(block)
            else:
                raise ValueError(block)
        return BlockStack(*blocks)
