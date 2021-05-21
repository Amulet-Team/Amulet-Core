from __future__ import annotations

from typing import Tuple, Generator

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
        super().__init__()
        self._uuid = _uuid
        self._position = position
        self._rotation = rotation

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def position(self) -> Tuple[float, float, float]:
        return self._position

    @property
    def rotation(self) -> Tuple[float, float]:
        return self._rotation


class PlayerManager(DatabaseHistoryManager):
    def __init__(self, level: api_level.BaseLevel):
        super().__init__()
        self._level = weakref.ref(level)

    @property
    def level(self) -> api_level.BaseLevel:
        return self._level()

    def get_players(self) -> Generator[str, None, None]:
        """
        Returns a generator of all player ids that are present in the level
        """
        yield from self.level.level_wrapper.get_players()

    def changed_players(self) -> Generator[str, None, None]:
        """The player objects that have changed since the last save"""
        yield from self.changed_entries()

    def has_player(self, player_id: str) -> bool:
        """
        Is the given player id present in the level

        :param player_id: The player id to check
        :return: True if the player id is present, False otherwise
        """
        return self._has_entry(player_id)

    def __contains__(self, item):
        """
        Is the given player id present in the level

        >>> '<uuid>' in level.players

        :param item: The player id to check
        :return: True if the player id is present, False otherwise
        """
        return self.has_player(item)

    def put_player(self, player: Player):
        self._put_entry(player.uuid, player)

    def get_player(self, player_id: str = LOCAL_PLAYER) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        return self._get_entry(player_id)

    def delete_player(self, player_id: str):
        """
        Deletes a player from the player manager

        :param player_id: The desired player id
        """
        self._delete_entry(player_id)

    def _get_entry_from_world(self, key: EntryKeyType) -> EntryType:
        return self.level.level_wrapper.get_player(key)
