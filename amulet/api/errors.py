class FormatError(Exception):
    """A base error for all errors related to the :class:`~amulet.api.wrapper.format_wrapper.FormatWrapper` class."""

    pass


class LoaderNoneMatched(FormatError):
    """An error thrown if no loader could be found that could load the given data."""

    pass


class BlockException(Exception):
    """An error thrown by the :class:`~amulet.api.block.Block` class."""

    pass


class EntryLoadError(Exception):
    pass


class EntryDoesNotExist(EntryLoadError):
    pass


class PlayerLoadError(EntryLoadError):
    """
    An error thrown if a player failed to load for some reason.
    """

    pass


class PlayerDoesNotExist(EntryDoesNotExist, PlayerLoadError):
    """
    An error thrown if a player does not exist.
    """

    pass


class ChunkLoadError(EntryLoadError):
    """
    An error thrown if a chunk failed to load for some reason.

    This may be due to a corrupt chunk, an unsupported chunk format or just because the chunk does not exist to be loaded.

    Catching this error will also catch :class:`ChunkDoesNotExist`

    >>> try:
    >>>     # get chunk
    >>>     chunk = world.get_chunk(cx, cz, dimension)
    >>> except ChunkLoadError:
    >>>     # will catch all chunks that have failed to load
    >>>     # either because they do not exist or errored during loading.
    """

    pass


class ChunkDoesNotExist(EntryDoesNotExist, ChunkLoadError):
    """
    An error thrown if a chunk does not exist and therefor cannot be loaded.

    >>> try:
    >>>     # get chunk
    >>>     chunk = world.get_chunk(cx, cz, dimension)
    >>> except ChunkDoesNotExist:
    >>>     # will catch all chunks that do not exist
    >>>     # will not catch corrupt chunks
    >>> except ChunkLoadError:
    >>>     # will only catch chunks that errored during loading
    >>>     # chunks that do not exist were caught by the previous except section.
    """

    pass


class ChunkSaveError(Exception):
    """An error thrown if there was an error during the chunk saving process."""

    pass


class DimensionDoesNotExist(Exception):
    """An error thrown if trying to load data from a dimension that does not exist."""

    pass


class ObjectReadWriteError(Exception):
    """
    An error thrown when the raw level data cannot be read from or written to.

    This is usually because the data has been opened somewhere else.
    """

    pass


class ObjectReadError(ObjectReadWriteError):
    """
    An error thrown when the raw level data cannot be read from.

    This is usually because the data has been opened somewhere else.
    """

    pass


class ObjectWriteError(ObjectReadWriteError):
    """
    An error thrown when the raw level data cannot be written to.

    This is usually because the data has been opened somewhere else.
    """

    pass
