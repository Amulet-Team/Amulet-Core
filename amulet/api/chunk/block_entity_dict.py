from collections import UserDict
from typing import Iterable, KeysView, ValuesView, ItemsView
import numpy

from amulet.api.data_types import BlockCoordinates
from amulet.api.block_entity import BlockEntity


class BlockEntityDict(UserDict):
    """
    A custom implementation of the dictionary class.

    It can only store :class:`BlockEntity` instances under the absolute coordinate of the block entity ``Tuple[int, int, int]``
    """

    InputType = Iterable[BlockEntity]

    def __init__(self, block_entities: InputType = ()):
        super().__init__()
        for block_entity in block_entities:
            self._assert_val(block_entity)
            self.data[block_entity.location] = block_entity

    def _assert_key(self, key):
        assert self._check_key(
            key
        ), f"Key must be in the format Tuple[int, int, int]. Got: {key}"

    @staticmethod
    def _check_key(key) -> bool:
        return (
            isinstance(key, tuple)
            and len(key) == 3
            and all(isinstance(a, (int, numpy.integer)) for a in key)
        )

    def _assert_val(self, value):
        assert self._check_val(value), f"Val must be a BlockEntity. Got: {value}"

    @staticmethod
    def _check_val(value) -> bool:
        return isinstance(value, BlockEntity)

    def __repr__(self) -> str:
        super_repr = (
            "".join(f"\n\t{key}:{val}" for key, val in self.data.items()) + "\n"
        )
        return f"BlockEntityDict({super_repr})"

    def clear(self) -> None:
        """Remove all block entities from the chunk."""
        self.data.clear()

    def keys(self) -> KeysView[BlockCoordinates]:
        """The location of every block entity in the chunk. Absolute coordinates."""
        return self.data.keys()

    def __iter__(self) -> Iterable[BlockEntity]:
        """
        An iterable of all the :class:`BlockEntity` objects.
        """
        yield from self.data.values()

    def values(self) -> ValuesView[BlockEntity]:
        """
        An iterable of all the :class:`BlockEntity` objects.
        """
        return self.data.values()

    def items(self) -> ItemsView[BlockCoordinates, BlockEntity]:
        """
        An iterable of all the locations and :class:`BlockEntity` objects.
        """
        return self.data.items()

    def copy(self) -> "BlockEntityDict":
        """
        Create a shallow copy of the block entity container.
        """
        return BlockEntityDict(self.values())

    def insert(self, block_entity: BlockEntity):
        """
        Insert the given :class:`BlockEntity` into the chunk at the location :attr:`BlockEntity.location`

        If a block entity already exists at this location it will be overwritten.

        :param block_entity: The block entity to add to the chunk.
        """
        self._assert_val(block_entity)
        self.data[block_entity.location] = block_entity

    def pop(self, coordinate: BlockCoordinates) -> BlockEntity:
        """
        Remove and return the :class:`BlockEntity` at ``coordinate``.

        :param coordinate: The coordinate to remove the block entity from.
        :return: The block entity at the specified coordinate.
        :raises:
            KeyError if there is no BlockEntity at the given coordinate.
        """
        self._assert_key(coordinate)
        if coordinate in self.data:
            return self.data.pop(coordinate)
        raise KeyError

    def __delitem__(self, coordinate: BlockCoordinates):
        """
        Remove the :class:`BlockEntity` at ``coordinate``.

        :param coordinate: The coordinate to remove the block entity from.
        """
        self._assert_key(coordinate)
        super().__delitem__(coordinate)

    def _check_block_entity(
        self, coordinate: BlockCoordinates, block_entity: BlockEntity
    ) -> BlockEntity:
        self._assert_key(coordinate)
        self._assert_val(block_entity)
        if coordinate != block_entity.location:
            block_entity = block_entity.new_at_location(*coordinate)
        return block_entity

    def __getitem__(self, coordinate: BlockCoordinates) -> BlockEntity:
        """
        Get the :class:`BlockEntity` at ``coordinate``.

        >>> block_entity = chunk.block_entities[(x, y, z)]

        :param coordinate: The coordinate to find the block entity at.
        :return: The block entity at the specified coordinate.
        :raises:
            KeyError if there is no BlockEntity at the given coordinate.
        """
        self._assert_key(coordinate)
        return super().__getitem__(coordinate)

    def __setitem__(self, coordinate: BlockCoordinates, block_entity: BlockEntity):
        """
        Set the :class:`BlockEntity` at ``coordinate``.

        >>> chunk.block_entities[(x, y, z)] = block_entity

        :param coordinate: The coordinate to set the block entity at.
        :param block_entity: The block entity to set at the specified coordinate.
        """
        self.data[coordinate] = self._check_block_entity(coordinate, block_entity)

    def setdefault(
        self, coordinate: BlockCoordinates, block_entity: BlockEntity
    ) -> BlockEntity:
        """
        Set the block entity at the given coordinate if there is not a block entity present.

        :param coordinate: The coordinate to set the block entity at.
        :param block_entity: The block entity to set at the specified coordinate if one is not present.
        """
        block_entity = self._check_block_entity(coordinate, block_entity)
        return self.data.setdefault(coordinate, block_entity)

    def popitem(self):
        raise NotImplementedError

    def update(self, block_entities: InputType):
        """
        Add the sequence of :class:`BlockEntity` instances to the chunk at the location :attr:`BlockEntity.location`

        If multiple block entities have the same coordinate only the last one will remain.

        :param block_entities: A sequence of :class:`BlockEntity` objects to add to the chunk.
        """
        for block_entity in block_entities:
            self._assert_val(block_entity)
            self.data[block_entity.location] = block_entity
