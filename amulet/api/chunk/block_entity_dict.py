from collections import UserDict
from typing import TYPE_CHECKING, Tuple, Iterable
import copy
from amulet.api.block_entity import BlockEntity

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

Coordinate = Tuple[int, int, int]


class BlockEntityDict(UserDict):
    InputType = Iterable[BlockEntity]

    def __init__(
        self,
        parent_chunk: "Chunk",
        block_entities: InputType = ()
    ):
        super(BlockEntityDict, self).__init__()
        for block_entity in block_entities:
            self._assert_val(block_entity)
            self.data[block_entity.location] = block_entity

        self._parent_chunk = parent_chunk

    def _assert_key(self, key):
        assert self._check_key(key)

    def _check_key(self, key):
        return isinstance(key, tuple) and all(isinstance(a, int) for a in key)

    def _assert_val(self, value):
        assert self._check_val(value)

    def _check_val(self, value):
        return isinstance(value, BlockEntity)

    def _dirty(self):
        self._parent_chunk.changed = True

    def __repr__(self) -> str:
        """ Return repr(self). """
        super_repr = "".join(f"\n\t{key}:{val}" for key, val in self.data.items()) + "\n"
        return f"BlockEntityDict({self._parent_chunk.cx},{self._parent_chunk.cz},{super_repr})"

    def clear(self) -> None:
        """ Remove all items from list. """
        self._dirty()
        self.data.clear()

    def __iter__(self):
        yield from self.data.values()

    def copy(self) -> "BlockEntityDict":
        return copy.deepcopy(self)

    def insert(self, block_entity: BlockEntity) -> None:
        """ Insert block_entity at its coordinates. """
        self._assert_val(block_entity)
        self._dirty()
        self.data[block_entity.location] = block_entity

    def pop(self, coordinate: Coordinate) -> BlockEntity:
        """
        Remove and return BlockEntity at coordinate.

        Raises IndexError if no BlockEntity at coordinate.
        """
        self._assert_key(coordinate)
        if coordinate in self.data:
            self._dirty()
            return self.data.pop(coordinate)
        raise IndexError

    def __delitem__(self, coordinate: Coordinate) -> None:
        """ Delete self[key]. """
        self._assert_key(coordinate)
        self._dirty()
        super().__delitem__(coordinate)

    def __setitem__(self, coordinate: Coordinate, block_entity: BlockEntity) -> None:
        """ Set self[key] to value. """
        self._assert_key(coordinate)
        self._assert_val(block_entity)
        self._dirty()
        self.data[coordinate] = block_entity

    def setdefault(self, coordinate: Coordinate, block_entity: BlockEntity) -> BlockEntity:
        self._assert_key(coordinate)
        self._assert_val(block_entity)
        self._dirty()
        self.data.setdefault(coordinate, block_entity)

    def popitem(self):
        raise NotImplementedError

    def update(self, block_entities: InputType) -> None:
        self._dirty()
        for block_entity in block_entities:
            self._assert_val(block_entity)
            self.data[block_entity.location] = block_entity


