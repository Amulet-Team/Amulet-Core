from typing import Iterable, Iterator
from collections.abc import MutableSet

from amulet.entity import Entity
from amulet.version import VersionRange, VersionRangeContainer


class EntityContainer(VersionRangeContainer, MutableSet[Entity]):
    def __init__(self, version_range: VersionRange):
        super().__init__(version_range)
        self._entities = set()

    def add(self, entity: Entity):
        if not isinstance(entity, Entity):
            raise TypeError("Expected an Entity")
        if entity.version not in self.version_range:
            raise ValueError(
                f"entity {entity} is incompatible with {self.version_range}"
            )
        self._entities.add(entity)

    def discard(self, entity: Entity) -> None:
        self._entities.discard(entity)

    def __contains__(self, entity: Entity) -> bool:
        return entity in self._entities

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self) -> Iterator[Entity]:
        yield from self._entities


class EntityComponent:
    """A chunk that supports entities"""

    def __init__(self, version_range: VersionRange):
        self.__entity = EntityContainer(version_range)

    @property
    def entity(self) -> EntityContainer:
        return self.__entity

    @entity.setter
    def entity(
        self,
        entities: Iterable[Entity],
    ):
        self.__entity.clear()
        for entity in entities:
            self.__entity.add(entity)
