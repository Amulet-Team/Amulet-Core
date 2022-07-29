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
        """Append value to the end of the list."""
        self._check_type(value)
        super().append(value)

    def copy(self) -> "ChunkList":
        raise NotImplementedError

    def extend(self, iterable: Iterable):
        """Extend list by appending elements from the iterable."""
        self._check_all_types(iterable)
        super().extend(iterable)

    def insert(self, index: int, value):
        """Insert value before index."""
        self._check_type(value)
        super().insert(index, value)

    def __repr__(self):
        if not self:
            return "[]"
        return "[" + "".join(f"\n\t{str(obj)}" for obj in self) + "\n]"


class EntityList(ChunkList):
    """
    A custom implementation of the list class.

    It can only store :class:`Entity` instances.
    """

    def __init__(self, entities: Iterable[Entity] = ()):
        """
        Construct an :class:`EntityList`.

        :param entities: An Iterable of :class:`Entity` objects.
        """
        for e in entities:
            self._check_type(e)
        super().__init__(entities)

    def _check_type(self, value):
        assert isinstance(value, Entity), f"{value} is not an instance of Entity"

    def copy(self) -> "EntityList":
        """
        Create a shallow copy of the entity container.
        """
        return EntityList(self)

    def __iter__(self) -> Iterable[Entity]:
        """
        An iterable of all the :class:`Entity` objects.
        """
        yield from self.data

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"EntityList({super().__repr__()})"
