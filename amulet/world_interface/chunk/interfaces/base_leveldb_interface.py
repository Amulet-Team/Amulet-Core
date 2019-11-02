from __future__ import annotations

from typing import Tuple, Union, Any

import struct
from amulet.world_interface.chunk.interfaces import Interface
from amulet.libs.leveldb import LevelDB
from amulet.world_interface.chunk import translators

# this is a dictionary of the last time each chunk version was written by a game version
chunk_version_to_max_version = {
    0: (1, 0, 0),
    1: (1, 0, 0),
    2: (1, 0, 0),
    3: (1, 0, 0),
    4: (1, 0, 0),
    5: (1, 0, 0),
    6: (1, 0, 0),
    7: (1, 0, 0),
    8: (1, 0, 0),
    9: (1, 0, 0),
    10: (1, 0, 0),
    11: (1, 0, 0),
    12: (1, 0, 0),
    13: (1, 0, 0),
    14: (1, 0, 0),
    15: (999, 999, 999)
}  # TODO: fill this list with the actual last game version number each chunk verison was last used in


class BaseLevelDBInterface(Interface):
    def get_translator(
        self,
        max_world_version: Tuple[str, Tuple[int, int, int]],
        data: Any = None,
    ) -> Tuple[translators.Translator, Tuple[int, int, int]]:
        """
        Get the Translator class for the requested version.
        :param max_world_version: The game version the world was last opened in.
        :type max_world_version: Java: int (DataVersion)    Bedrock: Tuple[int, int, int, ...] (game version number)
        :param data: Optional data to get translator based on chunk version rather than world version
        :param data: Any
        :return: Tuple[Translator, version number for PyMCTranslate to use]
        :rtype: Tuple[translators.Translator, Tuple[int, int, int]]
        """
        if data:
            key, max_chunk_version = self._get_translator_info(data)
            version = min(max_chunk_version, max_world_version[1])
        else:
            key = max_world_version
            version = max_world_version[1]
        return translators.loader.get(key), version

    def _get_translator_info(
        self, data: Tuple[int, int, LevelDB]
    ) -> Tuple[Tuple[str, int], Tuple[int, int, int]]:
        cx, cz, db = data
        chunk_version = db.get(struct.pack("<iic", cx, cz, b"v"))[0]
        chunk_max_version_number = chunk_version_to_max_version.get(chunk_version, (999, 999, 999))
        return ("leveldb", chunk_version), chunk_max_version_number
