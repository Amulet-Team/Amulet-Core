from typing import Iterable, Iterator
from collections.abc import MutableSet

from amulet.entity import Entity
from amulet.version import VersionRange, VersionRangeContainer
from amulet.utils.typed_property import TypedProperty


class EntityContainer(VersionRangeContainer, MutableSet[Entity]):
    _entities: set[Entity]

    def __init__(self, version_range: VersionRange):
        super().__init__(version_range)
        self._entities = set()

    def add(self, entity: Entity) -> None:
        if not isinstance(entity, Entity):
            raise TypeError("Expected an Entity")
        if entity.version not in self.version_range:
            raise ValueError(
                f"entity {entity} is incompatible with {self.version_range}"
            )
        self._entities.add(entity)

    def discard(self, entity: Entity) -> None:
        self._entities.discard(entity)

    def __contains__(self, entity: object) -> bool:
        return entity in self._entities

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self) -> Iterator[Entity]:
        yield from self._entities

    def __repr__(self) -> str:
        return f"EntityContainer({self.version_range!r}) # {len(self)} entities"


class EntityComponent:
    """A chunk that supports entities"""

    def __init__(self, version_range: VersionRange):
        self.__entities = EntityContainer(version_range)

    @TypedProperty[EntityContainer, Iterable[Entity]]
    def entities(self) -> EntityContainer:
        return self.__entities

    @entities.setter
    def _set_entity(
        self,
        entities: Iterable[Entity],
    ) -> None:
        self.__entities.clear()
        for entity in entities:
            self.__entities.add(entity)
