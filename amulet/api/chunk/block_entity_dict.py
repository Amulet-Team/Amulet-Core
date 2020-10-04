from collections import UserDict
from typing import Tuple, Iterable, Generator
import copy
import numpy

from amulet.api.block_entity import BlockEntity

Coordinate = Tuple[int, int, int]


class BlockEntityDict(UserDict):
    InputType = Iterable[BlockEntity]

    def __init__(self, block_entities: InputType = ()):
        super(BlockEntityDict, self).__init__()
        for block_entity in block_entities:
            self._assert_val(block_entity)
            self.data[block_entity.location] = block_entity

    def _assert_key(self, key):
        assert self._check_key(
            key
        ), f"Key must be in the format Tuple[int, int, int]. Got: {key}"

    @staticmethod
    def _check_key(key):
        return isinstance(key, tuple) and all(
            isinstance(a, (int, numpy.integer)) for a in key
        )

    def _assert_val(self, value):
        assert self._check_val(value), f"Val must be a BlockEntity. Got: {value}"

    @staticmethod
    def _check_val(value):
        return isinstance(value, BlockEntity)

    def __repr__(self) -> str:
        """ Return repr(self). """
        super_repr = (
            "".join(f"\n\t{key}:{val}" for key, val in self.data.items()) + "\n"
        )
        return f"BlockEntityDict({super_repr})"

    def clear(self) -> None:
        """ Remove all items from list. """
        self.data.clear()

    def keys(self) -> Generator[Coordinate, None, None]:
        yield from self.data.keys()

    def __iter__(self) -> Generator[BlockEntity, None, None]:
        yield from self.data.values()

    def values(self) -> Generator[BlockEntity, None, None]:
        yield from self.data.values()

    def items(self) -> Generator[Tuple[Coordinate, BlockEntity], None, None]:
        yield from self.data.items()

    def copy(self) -> "BlockEntityDict":
        return copy.deepcopy(self)

    def insert(self, block_entity: BlockEntity) -> None:
        """ Insert block_entity at its coordinates. """
        self._assert_val(block_entity)
        self.data[block_entity.location] = block_entity

    def pop(self, coordinate: Coordinate) -> BlockEntity:
        """
        Remove and return BlockEntity at coordinate.

        Raises IndexError if no BlockEntity at coordinate.
        """
        self._assert_key(coordinate)
        if coordinate in self.data:
            return self.data.pop(coordinate)
        raise IndexError

    def __delitem__(self, coordinate: Coordinate) -> None:
        """ Delete self[key]. """
        self._assert_key(coordinate)
        super().__delitem__(coordinate)

    def _check_block_entity(
        self, coordinate: Coordinate, block_entity: BlockEntity
    ) -> BlockEntity:
        self._assert_key(coordinate)
        self._assert_val(block_entity)
        if coordinate != block_entity.location:
            block_entity = block_entity.new_at_location(*coordinate)
        return block_entity

    def __setitem__(self, coordinate: Coordinate, block_entity: BlockEntity) -> None:
        """ Set self[key] to value. """
        self.data[coordinate] = self._check_block_entity(coordinate, block_entity)

    def setdefault(
        self, coordinate: Coordinate, block_entity: BlockEntity
    ) -> BlockEntity:
        block_entity = self._check_block_entity(coordinate, block_entity)
        return self.data.setdefault(coordinate, block_entity)

    def popitem(self):
        raise NotImplementedError

    def update(self, block_entities: InputType) -> None:
        for block_entity in block_entities:
            self._assert_val(block_entity)
            self.data[block_entity.location] = block_entity
