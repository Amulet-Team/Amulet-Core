from __future__ import annotations

from ...api.chunk import Chunk


class Format:
    def __init__(self, directory: str):
        self._directory = directory

    def get_chunk(self, cx: int, cz: int) -> Chunk:
        """
        Loads and creates an amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The chunk at the given coordinates.
        """
        raise NotImplementedError()

    @staticmethod
    def identify(directory: str) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError()
