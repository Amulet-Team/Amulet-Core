from __future__ import annotations

from . import component

__all__ = [
    "Chunk",
    "ChunkDoesNotExist",
    "ChunkLoadError",
    "component",
    "get_null_chunk",
]

class Chunk:
    """
    A base class for all chunk classes.
    """

    def reconstruct_chunk(self, arg0: dict[str, bytes | None]) -> None:
        """
        This is private. Do not use this. It will be removed in the future.
        """

    def serialise_chunk(self) -> dict[str, bytes | None]:
        """
        This is private. Do not use this. It will be removed in the future.
        """

    @property
    def chunk_id(self) -> str: ...
    @property
    def component_ids(self) -> set[str]: ...

class ChunkDoesNotExist(ChunkLoadError):
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

class ChunkLoadError(RuntimeError):
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

def get_null_chunk(arg0: str) -> Chunk:
    """
    This is a private function
    """
