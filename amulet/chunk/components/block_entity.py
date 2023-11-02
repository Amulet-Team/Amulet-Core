from __future__ import annotations
from collections.abc import MutableMapping
from typing import Iterable, Iterator

from amulet.api.data_types import BlockCoordinates
from amulet.block_entity import BlockEntity
from amulet.game_version import GameVersionRange, GameVersionRangeContainer


class BlockEntityContainer(GameVersionRangeContainer, MutableMapping[BlockCoordinates, BlockEntity]):
    """
    A MutableMapping that can only store :class:`BlockEntity` instances
    under the absolute coordinate of the block entity ``Tuple[int, int, int]``
    """

    def __init__(
        self,
        version_range: GameVersionRange,
    ):
        super().__init__(version_range)
        self._block_entities = {}

    def __setitem__(self, coordinate: BlockCoordinates, block_entity: BlockEntity):
        """
        Set the :class:`BlockEntity` at ``coordinate``.

        >>> block_entities: BlockEntityContainer
        >>> x = y = z = 0
        >>> block_entities[(x, y, z)] = block_entity

        :param coordinate: The coordinate to set the block entity at.
        :param block_entity: The block entity to set at the specified coordinate.
        """
        if (
            not isinstance(coordinate, tuple)
            and len(coordinate) == 3
            and all(isinstance(c, int) for c in coordinate)
        ):
            raise TypeError
        if not isinstance(block_entity, BlockEntity):
            raise TypeError
        if block_entity.version not in self.version_range:
            raise ValueError(f"block entity {block_entity} is incompatible with {self.version_range}")
        self._block_entities[coordinate] = block_entity

    def __delitem__(self, coordinate: BlockCoordinates):
        """
        Remove the :class:`BlockEntity` at ``coordinate``.

        :param coordinate: The coordinate to remove the block entity from.
        """
        del self._block_entities[coordinate]

    def __getitem__(self, coordinate: BlockCoordinates) -> BlockEntity:
        """
        Get the :class:`BlockEntity` at ``coordinate``.

        >>> block_entities: BlockEntityContainer
        >>> x = y = z = 0
        >>> block_entity = block_entities[(x, y, z)]

        :param coordinate: The coordinate to find the block entity at.
        :return: The block entity at the specified coordinate.
        :raises:
            KeyError if there is no BlockEntity at the given coordinate.
        """
        return self._block_entities[coordinate]

    def __len__(self) -> int:
        return len(self._block_entities)

    def __iter__(self) -> Iterator[BlockCoordinates]:
        yield from self._block_entities


class BlockEntityChunk:
    """A chunk that supports block entities"""

    def __init__(self, version_range: GameVersionRange):
        self.__block_entity = BlockEntityContainer(version_range)

    @property
    def block_entity(self) -> BlockEntityContainer:
        return self.__block_entity

    @block_entity.setter
    def block_entity(
        self,
        block_entities: Iterable[BlockCoordinates, BlockEntity],
    ):
        self.__block_entity.clear()
        for coord, block_entity in block_entities:
            self.__block_entity[coord] = block_entity
