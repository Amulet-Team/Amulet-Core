from __future__ import annotations
import amulet.block
import amulet.utils.collections
import amulet.version
import typing
__all__ = ['BlockPalette']
class BlockPalette:
    @typing.overload
    def __contains__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __contains__(self, arg0: amulet.block.BlockStack) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> amulet.block.BlockStack:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list:
        ...
    def __init__(self, arg0: amulet.version.VersionRange) -> None:
        ...
    def __iter__(self) -> amulet.utils.collections.PySequenceIterator:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __reversed__(self) -> amulet.utils.collections.PySequenceIterator:
        ...
    def block_stack_to_index(self, arg0: amulet.block.BlockStack) -> int:
        """
        Get the index of the block stack in the palette.
        If it is not in the palette already it will be added first.
        
        :param block_stack: The block stack to get the index of.
        :return: The index of the block stack in the palette.
        """
    def count(self, value: typing.Any) -> int:
        ...
    def index(self, value: typing.Any, start: int = 0, stop: int = 9223372036854775807) -> int:
        ...
    def index_to_block_stack(self, arg0: int) -> amulet.block.BlockStack:
        """
        Get the block stack at the specified palette index.
        
        :param index: The index to get
        :return: The block stack at that index
        :raises IndexError if there is no block stack at that index.
        """
