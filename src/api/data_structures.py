from __future__ import annotations

import copy
from collections import UserDict
from contextlib import AbstractContextManager
from typing import Sequence, Callable, TypeVar, Generic, Optional, Dict, List, Tuple

T = TypeVar("T")


class Stack(Generic[T]):
    """
    Implementation of a Stack, but prevents out-of-order editing of stored data
    """

    def __init__(self, initial_data: Sequence[T] = None):
        self._data = initial_data or []
        self.__contains__ = self._data.__contains__
        self.pop: Callable[[], T] = self._data.pop
        self.append: Callable[[T], None] = self._data.append
        self.size: Callable[[], int] = self._data.__len__

    def peek(self) -> Optional[T]:
        """
        Returns the top element of the Stack without removing it

        :return: The top element of the Stack, None if the Stack is empty
        """
        if self.is_empty():
            return None

        return self._data[-1]

    def is_empty(self) -> bool:
        """
        Checks if the Stack is empty

        :return: True is the Stack holds elements, False otherwise
        """
        return len(self._data) == 0

    def clear(self):
        """
        Clears all stored elements in the Stack
        """
        self._data.clear()


class EntityContext(AbstractContextManager):
    def __init__(self, mutable_entities, immutable_entities, chunks):
        self._entities: EntityContainer = mutable_entities
        self._old_entities: EntityContainer = copy.deepcopy(mutable_entities)
        self._immutable_entities = immutable_entities
        self._chunks = chunks
        self._changed = False

    @property
    def changed(self):
        return self._changed

    def __enter__(self):
        return self._entities

    def __exit__(self, exc_type, exc_value, traceback):
        if self._entities.data != self._old_entities.data:
            self._changed = True

            # TODO: Move the following re-organizing code to a more appropriate spot later
            changes = []
            for cx, cz in self._entities.dict_iter():
                contains_func = self._entity_in_chunk(cx, cz)
                in_chunk = list(filter(contains_func, self._entities[(cx, cz)]))
                out_of_chunk = list(
                    filter(
                        lambda ent: (not contains_func(ent)), self._entities[(cx, cz)]
                    )
                )

                if __debug__:
                    print(f"in_chunk ({cx}, {cz}):", in_chunk)
                    print(f"out_of_chunk ({cx}, {cz}):", out_of_chunk)

                self._entities[(cx, cz)] = in_chunk
                changes.extend(
                    list(
                        map(
                            lambda ent: (self._entity_chunk_coord(ent), ent),
                            out_of_chunk,
                        )
                    )
                )

            for chunk_coords, ent in changes:
                self._entities.setdefault(chunk_coords, []).append(ent)

            print("Entities changed!")

            for coords, chunk in self._chunks.items():
                chunk.entities = (
                    tuple(self._entities[coords]) + self._immutable_entities[coords]
                )
        else:
            print("Nothing changed!")
        return False

    @classmethod
    def _entity_chunk_coord(cls, ent):
        return int(ent["Pos"][0]) >> 4, int(ent["Pos"][2]) >> 4

    @classmethod
    def _entity_in_chunk(cls, cx, cz):
        def func(ent):
            x, z = cls._entity_chunk_coord(ent)
            return x == cx and z == cz

        return func


class EntityContainer(UserDict):
    data: Dict[Tuple[int, int], List]

    def dict_iter(self):
        return super(EntityContainer, self).__iter__()

    def __iter__(self):
        for coords, entities in self.data.items():
            yield from iter(entities)

    def add_entity(self, ent):
        x, y, z = [int(x) for x in ent["Pos"]]
        chunk_coords = (x >> 4, z >> 4)
        self.data.setdefault(chunk_coords, []).append(ent)

    def remove_entity(self, ent):
        x, y, z = ent["Pos"]
        chunk_coords = (x >> 4, z >> 4)
        if chunk_coords in self.data:
            self[chunk_coords].remove(ent)
