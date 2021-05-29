from __future__ import annotations

from typing import Generator, Set, Iterable, Dict

import weakref

from amulet.api.player import Player
from amulet.api.history.history_manager import DatabaseHistoryManager
from amulet.api.history.revision_manager import RAMRevisionManager
from amulet.api import level as api_level
from amulet.api.errors import PlayerLoadError, PlayerDoesNotExist


class PlayerManager(DatabaseHistoryManager):
    _temporary_database: Dict[str, Player]
    _history_database: Dict[str, RAMRevisionManager]

    DoesNotExistError = PlayerDoesNotExist
    LoadError = PlayerLoadError

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
        Returns a set of all player ids that are present in the level
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
        self._put_entry(player.player_id, player)

    def get_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        return self._get_entry(player_id)

    def _raw_get_entry(self, key: str) -> Player:
        return self.level.level_wrapper.load_player(key)

    def delete_player(self, player_id: str):
        """
        Deletes a player from the player manager

        :param player_id: The desired player id
        """
        self._delete_entry(player_id)
