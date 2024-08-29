from __future__ import annotations
import amulet_nbt
import collections.abc
import typing

__all__ = ["JavaRawChunkComponent"]

class JavaRawChunkComponent:
    ComponentID: typing.ClassVar[str] = "Amulet::JavaRawChunkComponent"
    @property
    def raw_data(self) -> collections.abc.MutableMapping[str, amulet_nbt.NamedTag]: ...
    @raw_data.setter
    def raw_data(
        self, arg1: collections.abc.Mapping[str, amulet_nbt.NamedTag]
    ) -> None: ...
