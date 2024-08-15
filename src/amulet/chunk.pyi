from __future__ import annotations

__all__ = ["Chunk"]

class Chunk:
    """
    A base class for all chunk classes.
    """

    @property
    def chunk_id(self) -> str: ...
