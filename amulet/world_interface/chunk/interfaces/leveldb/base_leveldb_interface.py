from __future__ import annotations

from typing import Tuple, Dict

from amulet.world_interface.chunk.interfaces import Interface
from amulet.world_interface.chunk import translators
from amulet.world_interface.chunk.interfaces.leveldb.leveldb_chunk_versions import chunk_to_game_version, game_to_chunk_version


class BaseLevelDBInterface(Interface):
    def get_translator(
        self,
        max_world_version: Tuple[str, Tuple[int, int, int]],
        data: Dict[bytes, bytes] = None,
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
            chunk_version = data[b'v'][0]
            game_version = chunk_to_game_version(max_world_version[1], chunk_version)
        else:
            game_version = max_world_version[1]
            chunk_version = game_to_chunk_version(game_version)
        return translators.loader.get(("leveldb", chunk_version)), game_version
