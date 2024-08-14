from __future__ import annotations

__all__ = ["Chunk"]

class Chunk:
    """
    A base class for all chunk classes.
    """

    def chunk_id(self) -> str: ...
