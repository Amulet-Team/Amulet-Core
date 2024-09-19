# from __future__ import annotations
#
# from collections.abc import MutableMapping
# from typing import Iterator, Any
#
# from amulet.data_types import BlockCoordinates
# from amulet.block_entity import BlockEntity
# from amulet.version import VersionRange, VersionRangeContainer
#
# from .abc import ChunkComponent, UnloadedComponent
#
#
# class BlockEntityComponentData(
#     VersionRangeContainer, MutableMapping[BlockCoordinates, BlockEntity]
# ):
#     """
#     A MutableMapping that can only store :class:`BlockEntity` instances
#     under the absolute coordinate of the block entity ``Tuple[int, int, int]``
#     """
#
#     _block_entities: dict[BlockCoordinates, BlockEntity]
#
#     def __init__(
#         self,
#         version_range: VersionRange,
#     ) -> None:
#         super().__init__(version_range)
#         self._block_entities = {}
#
#     def __getstate__(self) -> tuple[VersionRange, dict[BlockCoordinates, BlockEntity]]:  # type: ignore[override]
#         return (
#             super().__getstate__(),
#             self._block_entities,
#         )
#
#     def __setstate__(self, state: tuple[VersionRange, dict[BlockCoordinates, BlockEntity]]) -> None:  # type: ignore[override]
#         super().__setstate__(state[0])
#         self._block_entities = state[1]
#
#     def __setitem__(
#         self, coordinate: BlockCoordinates, block_entity: BlockEntity
#     ) -> None:
#         """
#         Set the :class:`BlockEntity` at ``coordinate``.
#
#         >>> block_entities: BlockEntityComponentData
#         >>> x = y = z = 0
#         >>> block_entities[(x, y, z)] = block_entity
#
#         :param coordinate: The coordinate to set the block entity at.
#         :param block_entity: The block entity to set at the specified coordinate.
#         """
#         if (
#             not isinstance(coordinate, tuple)
#             and len(coordinate) == 3
#             and all(isinstance(c, int) for c in coordinate)
#         ):
#             raise TypeError
#         if not isinstance(block_entity, BlockEntity):
#             raise TypeError
#         if not self.version_range.contains(block_entity.platform, block_entity.version):
#             raise ValueError(
#                 f"block entity {block_entity} is incompatible with {self.version_range}"
#             )
#         self._block_entities[coordinate] = block_entity
#
#     def __delitem__(self, coordinate: BlockCoordinates) -> None:
#         """
#         Remove the :class:`BlockEntity` at ``coordinate``.
#
#         :param coordinate: The coordinate to remove the block entity from.
#         """
#         del self._block_entities[coordinate]
#
#     def __getitem__(self, coordinate: BlockCoordinates) -> BlockEntity:
#         """
#         Get the :class:`BlockEntity` at ``coordinate``.
#
#         >>> block_entities: BlockEntityComponentData
#         >>> x = y = z = 0
#         >>> block_entity = block_entities[(x, y, z)]
#
#         :param coordinate: The coordinate to find the block entity at.
#         :return: The block entity at the specified coordinate.
#         :raises:
#             KeyError if there is no BlockEntity at the given coordinate.
#         """
#         return self._block_entities[coordinate]
#
#     def __len__(self) -> int:
#         return len(self._block_entities)
#
#     def __iter__(self) -> Iterator[BlockCoordinates]:
#         yield from self._block_entities
#
#     def __repr__(self) -> str:
#         return (
#             f"BlockEntityContainer({self.version_range!r}) # {len(self)} block entities"
#         )
#
#
# class BlockEntityComponent(
#     ChunkComponent[BlockEntityComponentData, BlockEntityComponentData]
# ):
#     storage_key = b"be"
#
#     @staticmethod
#     def fix_set_data(
#         old_obj: BlockEntityComponentData | UnloadedComponent,
#         new_obj: BlockEntityComponentData,
#     ) -> BlockEntityComponentData:
#         if not isinstance(new_obj, BlockEntityComponentData):
#             raise TypeError
#         assert isinstance(old_obj, BlockEntityComponentData)
#         if old_obj.version_range != new_obj.version_range:
#             raise ValueError("New version range does not match old version range.")
#         return new_obj
