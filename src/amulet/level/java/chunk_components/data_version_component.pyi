from __future__ import annotations
import typing

__all__ = ["DataVersionComponent"]

class DataVersionComponent:
    ComponentID: typing.ClassVar[str] = "Amulet::DataVersionComponent"
    @property
    def data_version(self) -> int: ...
