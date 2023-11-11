from _typeshed import Incomplete
from amulet.block import BlockStack as BlockStack
from amulet.version import VersionRange as VersionRange, VersionRangeContainer as VersionRangeContainer
from collections.abc import Sequence
from typing import Union

class BlockPalette(VersionRangeContainer, Sequence[BlockStack]):
    """
    Class to handle the mappings between Block Stack objects and their index-based internal IDs
    """
    _lock: Incomplete
    _index_to_block: Incomplete
    _block_to_index: Incomplete
    def __init__(self, version_range: VersionRange) -> None:
        """
        Creates a new BlockPalette object
        """
    def __len__(self) -> int:
        """
        The number of block stacks in the palette.

        >>> block_palette: BlockPalette
        >>> len(block_palette)
        10
        """
    def __getitem__(self, item): ...
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
    def index_to_block_stack(self, index: int) -> BlockStack:
        """
        Get the block stack at the specified palette index.
        :param index: The index to get
        :return: The block stack at that index
        :raises KeyError if there is no block stack at that index.
        """
    def block_stack_to_index(self, block_stack: BlockStack) -> int:
        """
        Get the index of the block stack in the palette.
        If it is not in the palette already it will be added first.
        :param block_stack: The block stack to get the index of.
        :return: The index of the block stack in the palette.
        """
