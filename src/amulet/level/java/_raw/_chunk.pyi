from __future__ import annotations
import amulet.chunk
import amulet_nbt
import typing

__all__ = ["decode_chunk", "encode_chunk"]

def decode_chunk(
    arg0: typing.Any,
    arg1: typing.Any,
    arg2: dict[str, amulet_nbt.NamedTag],
    arg3: int,
    arg4: int,
) -> amulet.chunk.Chunk: ...
def encode_chunk(
    arg0: typing.Any, arg1: typing.Any, arg2: amulet.chunk.Chunk, arg3: int, arg4: int
) -> dict[str, amulet_nbt.NamedTag]: ...
