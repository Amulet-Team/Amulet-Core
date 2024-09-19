from __future__ import annotations

import collections.abc
import typing

import amulet_nbt

__all__ = ["DataVersionComponent", "JavaRawChunkComponent"]

class DataVersionComponent:
    ComponentID: typing.ClassVar[str] = "Amulet::DataVersionComponent"
    @property
    def data_version(self) -> int: ...

class JavaRawChunkComponent:
    ComponentID: typing.ClassVar[str] = "Amulet::JavaRawChunkComponent"
    @property
    def raw_data(self) -> collections.abc.MutableMapping[str, amulet_nbt.NamedTag]: ...
    @raw_data.setter
    def raw_data(
        self, arg1: collections.abc.Mapping[str, amulet_nbt.NamedTag]
    ) -> None: ...
