from __future__ import annotations

__all__ = ["Chunk", "get_null_chunk"]

class Chunk:
    """
    A base class for all chunk classes.
    """

    def __getstate__(self) -> tuple: ...
    def __setstate__(self, arg0: tuple) -> None: ...
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
    def component_ids(self) -> list[str]: ...

def get_null_chunk(arg0: str) -> Chunk:
    """
    This is a private function
    """
