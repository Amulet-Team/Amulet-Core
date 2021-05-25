from __future__ import annotations

from typing import Tuple, Generator, Set, Iterable

import weakref

from amulet.api.history import Changeable
from amulet.api.history.data_types import EntryKeyType, EntryType
from amulet.api.history.history_manager import DatabaseHistoryManager
from amulet.api import level as api_level

LOCAL_PLAYER = "~local_player"


class Player(Changeable):
    def __init__(
        self,
        _uuid: str,
        position: Tuple[float, float, float],
        rotation: Tuple[float, float],
    ):
        """
        Creates a new instance of :class:`Player` with the given UUID, position, and rotation

        :param _uuid: The UUID of the player
        :param position: The position of the player in world coordinates
        :param rotation: The rotation of the player
        """
        super().__init__()
        self._uuid = _uuid
        self._position = position
        self._rotation = rotation

    @property
    def uuid(self) -> str:
        """The player's UUID"""
        return self._uuid

    @property
    def position(self) -> Tuple[float, float, float]:
        """The current position of the player in the world"""
        return self._position

    @property
    def rotation(self) -> Tuple[float, float]:
        """The current rotation of the player in the world"""
        return self._rotation


class PlayerManager(DatabaseHistoryManager):
    def __init__(self, level: api_level.BaseLevel):
        """
        Construct a new :class:`PlayerManager` instance

        This should not be used by third party code

        :param level: The world that this player manager is associated with
        """
        super().__init__()
        self._level = weakref.ref(level)

    @property
    def level(self) -> api_level.BaseLevel:
        """The level that this player manager is associated with."""
        return self._level()

    def all_player_ids(self) -> Set[str]:
        """
        Returns a generator of all player ids that are present in the level
        """
        return self._all_entries()

    def _raw_all_entries(self) -> Iterable[str]:
        return self.level.level_wrapper.all_player_ids()

    def changed_players(self) -> Generator[str, None, None]:
        """The player objects that have changed since the last save"""
        return self.changed_entries()

    def has_player(self, player_id: str) -> bool:
        """
        Is the given player id present in the level

        :param player_id: The player id to check
        :return: True if the player id is present, False otherwise
        """
        return self._has_entry(player_id)

    def _raw_has_entry(self, key: str) -> bool:
        return self.level.level_wrapper.has_player(key)

    def __contains__(self, item):
        """
        Is the given player id present in the level

        >>> '<uuid>' in level.players

        :param item: The player id to check
        :return: True if the player id is present, False otherwise
        """
        return self.has_player(item)

    def put_player(self, player: Player):
        """
        Add the given player to the player manager.

        :param player: The :class:`Player` object to add to the chunk manager. It will be added with the key designated by :attr:`Player.uuid`
        """
        self._put_entry(player.uuid, player)

    def get_player(self, player_id: str = LOCAL_PLAYER) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        return self._get_entry(player_id)

    def _raw_get_entry(self, key: EntryKeyType) -> EntryType:
        return self.level.level_wrapper.get_player(key)

    def delete_player(self, player_id: str):
        """
        Deletes a player from the player manager

        :param player_id: The desired player id
        """
        self._delete_entry(player_id)
