from collections import UserList
from typing import Iterable
from amulet.api.entity import Entity


class ChunkList(UserList):
    def __init__(self, iterable: Iterable = ()):
        super().__init__(list(iterable))

    def _check_all_types(self, value):
        for val in value:
            self._check_type(val)

    def _check_type(self, value):
        raise NotImplementedError

    def append(self, value) -> None:
        """ Append value to the end of the list. """
        self._check_type(value)
        super().append(value)

    def copy(self) -> "ChunkList":
        raise NotImplementedError

        """ Extend list by appending elements from the iterable. """
    def extend(self, iterable: Iterable):
        self._check_all_types(iterable)
        super().extend(iterable)

        """ Insert value before index. """
    def insert(self, index: int, value):
        self._check_type(value)
        super().insert(index, value)

    def __repr__(self):
        if not self:
            return "[]"
        return "[" + "".join(f"\n\t{str(obj)}" for obj in self) + "\n]"


class EntityList(ChunkList):

    def __init__(self, entities: Iterable[Entity] = ()):
        for e in entities:
            self._check_type(e)
        super().__init__(entities)

    def _check_type(self, value):
        assert isinstance(value, Entity), f"{value} is not an instance of Entity"

    def copy(self) -> "EntityList":
        return EntityList(self)

    def __iter__(self) -> Iterable[Entity]:
        yield from self.data

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
