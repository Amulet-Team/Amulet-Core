# from __future__ import annotations
# from typing import Iterator, Any
# from collections.abc import MutableSet
#
# from amulet.entity import Entity
# from amulet.version import VersionRange, VersionRangeContainer
# from .abc import ChunkComponent
#
#
# class EntityComponentData(VersionRangeContainer, MutableSet[Entity]):
#     _entities: set[Entity]
#
#     def __init__(self, version_range: VersionRange):
#         super().__init__(version_range)
#         self._entities = set()
#
#     def __getstate__(self) -> tuple[VersionRange, set[Entity]]:  # type: ignore[override]
#         return (
#             super().__getstate__(),
#             self._entities,
#         )
#
#     def __setstate__(self, state: tuple[VersionRange, set[Entity]]) -> None:  # type: ignore[override]
#         super().__setstate__(state[0])
#         self._entities = state[1]
#
#     def add(self, entity: Entity) -> None:
#         if not isinstance(entity, Entity):
#             raise TypeError("Expected an Entity")
#         if not self.version_range.contains(entity.platform, entity.version):
#             raise ValueError(
#                 f"entity {entity} is incompatible with {self.version_range}"
#             )
#         self._entities.add(entity)
#
#     def discard(self, entity: Entity) -> None:
#         self._entities.discard(entity)
#
#     def __contains__(self, entity: object) -> bool:
#         return entity in self._entities
#
#     def __len__(self) -> int:
#         return len(self._entities)
#
#     def __iter__(self) -> Iterator[Entity]:
#         yield from self._entities
#
#     def __repr__(self) -> str:
#         return f"EntityContainer({self.version_range!r}) # {len(self)} entities"
#
#
# class EntityComponent(ChunkComponent[EntityComponentData, EntityComponentData]):
#     storage_key = b"e"
#
#     @staticmethod
#     def fix_set_data(
#         old_obj: EntityComponentData, new_obj: EntityComponentData
#     ) -> EntityComponentData:
#         if not isinstance(new_obj, EntityComponentData):
#             raise TypeError
#         assert isinstance(old_obj, EntityComponentData)
#         if old_obj.version_range != new_obj.version_range:
#             raise ValueError("New version range does not match old version range.")
#         return new_obj
