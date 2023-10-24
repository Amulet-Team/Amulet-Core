from __future__ import annotations

from typing import Any


class NativeChunk:
    def __init__(self):
        pass

    @classmethod
    def from_raw(cls, raw_chunk: Any) -> NativeChunk:
        """
        Load the raw data into a native chunk instance.
        This will error if the raw data is not the correct format.
        """
        raise NotImplementedError

    def to_raw(self) -> Any:
        """Pack this native chunk instance into the raw format."""
        raise NotImplementedError

    @classmethod
    def from_universal(cls, universal_chunk) -> NativeChunk:
        """
        Convert the universal chunk to this native chunk format.
        This is an implementation detail and must not be used by third party code.
        """
        raise NotImplementedError

    def to_universal(self):
        """
        Convert the native chunk to a universal chunk.
        This is an implementation detail and must not be used by third party code.
        """
        raise NotImplementedError
