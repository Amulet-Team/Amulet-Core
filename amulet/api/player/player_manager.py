from __future__ import annotations

import weakref

from amulet.api.history import Changeable
from amulet.api.history.data_types import EntryKeyType, EntryType
from amulet.api.history.history_manager import DatabaseHistoryManager


class Player(Changeable):
    def __init__(self, nbt_data):
        super().__init__()
        self._nbt = nbt_data
        print(self._nbt)

    @property
    def position(self):
        return tuple(map(lambda t: t.value, self._nbt["Pos"]))

    @property
    def rotation(self):
        return tuple(map(lambda t: t.value, self._nbt["Rotation"]))


class PlayerManager(DatabaseHistoryManager):
    def __init__(self, level):
        super().__init__()
        self._level = weakref.ref(level)

    @property
    def level(self) -> "amulet.api.level.BaseLevel":
        return self._level()

    def get_players(self):
        yield from self.level.level_wrapper.get_players()

    def changed_players(self):
        yield from self.changed_entries()

    def has_player(self, uuid):
        return self._has_entry(uuid)

    def __contains__(self, item):
        return self.has_player(item)

    def put_player(self, player):
        self._put_entry(player.uuid, player)

    def get_player(self, uuid):
        return self._get_entry(uuid)

    def delete_player(self, uuid):
        self._delete_entry(uuid)

    def _get_entry_from_world(self, key: EntryKeyType) -> EntryType:
        print(f"entry: {key}")
        return self.level.level_wrapper.get_player(key)
