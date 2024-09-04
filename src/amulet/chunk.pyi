from __future__ import annotations

__all__ = ["Chunk", "get_null_chunk"]

class Chunk:
    """
    A base class for all chunk classes.
    """

    @property
    def chunk_id(self) -> str: ...
def get_null_chunk(arg0: str) -> Chunk:
    """
    This is a private function
    """
