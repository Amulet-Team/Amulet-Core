from typing import Any, Self, TypeAlias, cast
from types import UnionType

from amulet.chunk import Chunk


class JavaChunk0(Chunk):
    @classmethod
    def new(cls, *args: Any, **kwargs: Any) -> Self:
        pass


class JavaChunk1444(Chunk):
    @classmethod
    def new(cls, *args: Any, **kwargs: Any) -> Self:
        pass


# TODO: Improve this if python/mypy#11673 gets fixed.
JavaChunk: TypeAlias = cast(UnionType, JavaChunk0 | JavaChunk1444)
