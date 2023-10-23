from typing import Iterable, Iterator
from amulet.entity import Entity
from collections.abc import MutableSet


class EntityContainer(MutableSet[Entity]):
    def __init__(self, entities: Iterable[Entity] = ()):
        self._entities = set(entities)

    def add(self, entity: Entity):
        if not isinstance(entity, Entity):
            raise TypeError("Expected an Entity")
        self._entities.add(entity)

    def discard(self, entity: Entity) -> None:
        self._entities.discard(entity)

    def __contains__(self, entity: Entity) -> bool:
        return entity in self._entities

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self) -> Iterator[Entity]:
        yield from self._entities


class EntityChunk:
    """A chunk that supports entities"""

    def __init__(self):
        self.__entity = EntityContainer()

    @property
    def entity(self) -> EntityContainer:
        return self.__entity

    @entity.setter
    def entity(
        self,
        entities: Iterable[Entity],
    ):
        self.__entity = EntityContainer(entities)
