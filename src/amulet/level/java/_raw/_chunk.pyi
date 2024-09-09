from __future__ import annotations

import typing

import amulet.level.java.chunk
import amulet_nbt

__all__ = ["decode_chunk", "encode_chunk"]

def decode_chunk(
    arg0: typing.Any,
    arg1: typing.Any,
    arg2: dict[str, amulet_nbt.NamedTag],
    arg3: int,
    arg4: int,
) -> amulet.level.java.chunk.JavaChunk: ...
def encode_chunk(
    arg0: typing.Any,
    arg1: typing.Any,
    arg2: amulet.level.java.chunk.JavaChunk,
    arg3: int,
    arg4: int,
) -> dict[str, amulet_nbt.NamedTag]: ...
