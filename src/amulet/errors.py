# TODO: move all references to chunk
from .chunk import ChunkLoadError, ChunkDoesNotExist

class DimensionDoesNotExist(Exception):
    """An error thrown if trying to load data from a dimension that does not exist."""


class PlayerLoadError(Exception):
    """
    An error thrown if a player failed to load for some reason.
    """


class PlayerDoesNotExist(PlayerLoadError):
    """
    An error thrown if a player does not exist.
    """


class LevelReadError(Exception):
    """
    An error thrown when the raw level data cannot be read from.

    This is usually because the data has been opened somewhere else.
    """


class LevelWriteError(Exception):
    """
    An error thrown when the raw level data cannot be written to.

    This is usually because the data has been opened somewhere else.
    """
