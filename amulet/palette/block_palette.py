from __future__ import annotations

from amulet.block import BlockStack
from ._palette import Palette


class BlockPalette(Palette[BlockStack]):
    """
    Class to handle the mappings between Block Stack objects and their index-based internal IDs
    """

    def _is_item(self, item: BlockStack) -> bool:
        return isinstance(item, BlockStack)

    def index_to_block_stack(self, index: int) -> BlockStack:
        """
        Get the block stack at the specified palette index.
        :param index: The index to get
        :return: The block stack at that index
        :raises KeyError if there is no block stack at that index.
        """
        return self._index_to_item[index]

    def block_stack_to_index(self, block_stack: BlockStack) -> int:
        """
        Get the index of the block stack in the palette.
        If it is not in the palette already it will be added first.
        :param block_stack: The block stack to get the index of.
        :return: The index of the block stack in the palette.
        """
        if not isinstance(block_stack, BlockStack):
            raise TypeError(repr(block_stack))
        if not all(self.version_range.contains(block.platform, block.version) for block in block_stack):
            raise ValueError(
                f"BlockStack {block_stack} is incompatible with {self.version_range}"
            )
        return self._get_index(block_stack)

    def __repr__(self) -> str:
        return f"BlockPalette({self.version_range!r}) # {len(self)} blocks"
