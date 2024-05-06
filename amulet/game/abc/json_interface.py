from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self, Union, TypeAlias

JSONCompatible: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
    "JSONList",
    "JSONDict",
]
JSONDict: TypeAlias = dict[str, "JSONCompatible"]
JSONList: TypeAlias = list["JSONCompatible"]


class JSONInterface(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, obj: JSONCompatible) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> JSONCompatible:
        raise NotImplementedError
