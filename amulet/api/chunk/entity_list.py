from collections import UserList
from typing import TYPE_CHECKING, Iterable, Union, overload, Any
import copy
from amulet.api.entity import Entity
import weakref

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class ChunkList(UserList):
    def __init__(self, parent_chunk: "Chunk", iterable: Iterable = ()):
        super(ChunkList, self).__init__(list(iterable))
        self._parent_chunk = weakref.ref(parent_chunk)

    def _check_all_types(self, value):
        [self._check_type(val) for val in value]

    def _check_type(self, value):
        raise NotImplementedError

    def _dirty(self):
        self._parent_chunk().changed = True

    def append(self, value) -> None:
        """ Append value to the end of the list. """
        self._check_type(value)
        self._dirty()
        super().append(value)

    def clear(self) -> None:
        """ Remove all items from list. """
        self._dirty()
        super().clear()

    def copy(self) -> "ChunkList":
        return copy.deepcopy(self)

    def extend(self, iterable: Iterable) -> None:
        """ Extend list by appending elements from the iterable. """
        self._check_all_types(iterable)
        self._dirty()
        super().extend(iterable)

    def insert(self, index: int, value) -> None:
        """ Insert value before index. """
        self._check_type(value)
        self._dirty()
        super().insert(index, value)

    def pop(self, index: int = -1) -> Any:
        """
        Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        self._dirty()
        return super().pop(index)

    def remove(self, value) -> None:
        """
        Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        self._dirty()
        super().remove(value)

    def reverse(self) -> None:
        """ Reverse *IN PLACE*. """
        self._dirty()
        super().reverse()

    def sort(self, *args, **kwargs):
        """ Stable sort *IN PLACE*. """
        self._dirty()
        super().sort(*args, **kwargs)

    def __delitem__(self, i: Union[int, slice]) -> None:
        """ Delete self[key]. """
        self._dirty()
        super().__delitem__(i)

    def __iadd__(self, x: "ChunkList") -> "ChunkList":
        """ Implement self+=value. """
        self._dirty()
        return super().__iadd__(x)

    def __imul__(self, n: int) -> "ChunkList":
        """ Implement self*=value. """
        self._dirty()
        return super().__imul__(n)

    @overload
    def __setitem__(self, i: int, o) -> None:
        ...

    def __setitem__(self, i: slice, o: Iterable) -> None:
        """ Set self[key] to value. """
        self._dirty()
        super().__setitem__(i, o)

    def __repr__(self):
        if not self:
            return "[]"
        return "".join(f"\n\t{str(obj)}" for obj in self) + "\n"


class EntityList(ChunkList):
    def _check_type(self, value):
        assert isinstance(value, Entity)

    def __repr__(self) -> str:
        """ Return repr(self). """
        return f"EntityList({self._parent_chunk().cx},{self._parent_chunk().cz},{super().__repr__()})"


if __name__ == "__main__":
    import amulet_nbt
    from amulet.api.chunk import Chunk

    c = Chunk(0, 0)
    print(
        c.entities.__class__
    )  # this is <class 'amulet.api.chunk.chunk_list.EntityList'>
    print(isinstance(c.entities, EntityList))  # but this is false. WHY???????
    block_ents = [
        Entity("minecraft", "creeper", 0, 0, 0, amulet_nbt.NBTFile()),
        Entity("minecraft", "cow", 0, 0, 0, amulet_nbt.NBTFile()),
        Entity("minecraft", "pig", 0, 0, 0, amulet_nbt.NBTFile()),
        Entity("minecraft", "sheep", 0, 0, 0, amulet_nbt.NBTFile()),
    ]
    c.entities.append(Entity("minecraft", "cow", 0, 0, 0, amulet_nbt.NBTFile()))
    c.entities += block_ents
    print(c.entities)
