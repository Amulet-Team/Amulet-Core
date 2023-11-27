from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self


JSONCompatible = (
    str
    | int
    | float
    | bool
    | None
    | "JSONList"
    | tuple["JSONCompatible", ...]
    | "JSONDict"
)

JSONDict = dict[str, "JSONCompatible"]
JSONList = list["JSONCompatible"]


class JSONInterface(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, obj: JSONCompatible) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> JSONCompatible:
        raise NotImplementedError
