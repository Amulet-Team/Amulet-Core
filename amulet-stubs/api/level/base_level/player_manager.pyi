from _typeshed import Incomplete
from amulet.api import level as api_level
from amulet.api.errors import PlayerDoesNotExist as PlayerDoesNotExist, PlayerLoadError as PlayerLoadError
from amulet.api.history.history_manager import DatabaseHistoryManager as DatabaseHistoryManager
from amulet.api.history.revision_manager import RAMRevisionManager as RAMRevisionManager
from amulet.player import Player as Player
from typing import Dict, Generator, Iterable, Set

class PlayerManager(DatabaseHistoryManager):
    _temporary_database: Dict[str, Player]
    _history_database: Dict[str, RAMRevisionManager]
    DoesNotExistError = PlayerDoesNotExist
    LoadError = PlayerLoadError
    _level: Incomplete
    def __init__(self, level: api_level.BaseLevel) -> None:
        """
        Construct a new :class:`PlayerManager` instance

        This should not be used by third party code

        :param level: The world that this player manager is associated with
        """
    @property
    def level(self) -> api_level.BaseLevel:
        """The level that this player manager is associated with."""
    def all_player_ids(self) -> Set[str]:
        """
        Returns a set of all player ids that are present in the level
        """
    def _raw_all_entries(self) -> Iterable[str]: ...
    def changed_players(self) -> Generator[str, None, None]:
        """The player objects that have changed since the last save"""
    def has_player(self, player_id: str) -> bool:
        """
        Is the given player id present in the level

        :param player_id: The player id to check
        :return: True if the player id is present, False otherwise
        """
    def _raw_has_entry(self, key: str) -> bool: ...
    def __contains__(self, item) -> bool:
        """
        Is the given player id present in the level

        >>> '<uuid>' in level.players

        :param item: The player id to check
        :return: True if the player id is present, False otherwise
        """
    def put_player(self, player: Player):
        """
        Add the given player to the player manager.

        :param player: The :class:`Player` object to add to the chunk manager. It will be added with the key designated by :attr:`Player.uuid`
        """
    def get_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
    def _raw_get_entry(self, key: str) -> Player: ...
    def delete_player(self, player_id: str):
        """
        Deletes a player from the player manager

        :param player_id: The desired player id
        """
