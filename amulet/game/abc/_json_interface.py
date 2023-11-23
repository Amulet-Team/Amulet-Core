from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self


JSONCompatible = (
    str
    | int
    | float
    | bool
    | None
    | list["JSONCompatible"]
    | tuple["JSONCompatible", ...]
    | dict[str, "JSONCompatible"]
)


class JSONInterface(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, obj: dict[str, JSONCompatible]) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, JSONCompatible]:
        raise NotImplementedError
