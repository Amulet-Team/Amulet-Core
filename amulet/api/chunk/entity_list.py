from collections import UserList
from typing import Iterable, Generator
import copy
from amulet.api.entity import Entity


class ChunkList(UserList):
    def __init__(self, iterable: Iterable = ()):
        super(ChunkList, self).__init__(list(iterable))

    def _check_all_types(self, value):
        [self._check_type(val) for val in value]

    def _check_type(self, value):
        raise NotImplementedError

    def append(self, value) -> None:
        """ Append value to the end of the list. """
        self._check_type(value)
        super().append(value)

    def copy(self) -> "ChunkList":
        return copy.deepcopy(self)

    def extend(self, iterable: Iterable[Entity]) -> None:
        """ Extend list by appending elements from the iterable. """
        self._check_all_types(iterable)
        super().extend(iterable)

    def insert(self, index: int, value) -> None:
        """ Insert value before index. """
        self._check_type(value)
        super().insert(index, value)

    def __repr__(self):
        if not self:
            return "[]"
        return "".join(f"\n\t{str(obj)}" for obj in self) + "\n"


class EntityList(ChunkList):
    def _check_type(self, value):
        assert isinstance(value, Entity)

    def __iter__(self) -> Generator[Entity, None, None]:
        yield from super().__iter__()

    def __repr__(self) -> str:
        """ Return repr(self). """
        return f"EntityList({super().__repr__()})"


if __name__ == "__main__":
    import amulet_nbt

    entities = EntityList()
    block_ents = [
        Entity("minecraft", "creeper", 0.0, 0.0, 0.0, amulet_nbt.NBTFile()),
        Entity("minecraft", "cow", 0.0, 0.0, 0.0, amulet_nbt.NBTFile()),
        Entity("minecraft", "pig", 0.0, 0.0, 0.0, amulet_nbt.NBTFile()),
        Entity("minecraft", "sheep", 0.0, 0.0, 0.0, amulet_nbt.NBTFile()),
    ]
    entities.append(Entity("minecraft", "cow", 0.0, 0.0, 0.0, amulet_nbt.NBTFile()))
    entities += block_ents
    print(entities)
