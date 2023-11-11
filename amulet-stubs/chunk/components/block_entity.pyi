from _typeshed import Incomplete
from amulet.api.data_types import BlockCoordinates as BlockCoordinates
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.version import VersionRange as VersionRange, VersionRangeContainer as VersionRangeContainer
from collections.abc import MutableMapping
from typing import Iterable, Iterator

class BlockEntityContainer(VersionRangeContainer, MutableMapping[BlockCoordinates, BlockEntity]):
    """
    A MutableMapping that can only store :class:`BlockEntity` instances
    under the absolute coordinate of the block entity ``Tuple[int, int, int]``
    """
    _block_entities: Incomplete
    def __init__(self, version_range: VersionRange) -> None: ...
    def __setitem__(self, coordinate: BlockCoordinates, block_entity: BlockEntity):
        """
        Set the :class:`BlockEntity` at ``coordinate``.

        >>> block_entities: BlockEntityContainer
        >>> x = y = z = 0
        >>> block_entities[(x, y, z)] = block_entity

        :param coordinate: The coordinate to set the block entity at.
        :param block_entity: The block entity to set at the specified coordinate.
        """
    def __delitem__(self, coordinate: BlockCoordinates):
        """
        Remove the :class:`BlockEntity` at ``coordinate``.

        :param coordinate: The coordinate to remove the block entity from.
        """
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
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[BlockCoordinates]: ...

class BlockEntityComponent:
    """A chunk that supports block entities"""
    __block_entity: Incomplete
    def __init__(self, version_range: VersionRange) -> None: ...
    @property
    def block_entity(self) -> BlockEntityContainer: ...
    @block_entity.setter
    def block_entity(self, block_entities: Iterable[BlockCoordinates, BlockEntity]): ...
