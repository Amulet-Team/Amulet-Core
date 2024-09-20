import abc
from abc import ABC, abstractmethod
from typing import Self, TypeAlias

JSONCompatible: TypeAlias
JSONDict: TypeAlias
JSONList: TypeAlias

class JSONInterface(ABC, metaclass=abc.ABCMeta):
    @classmethod
    @abstractmethod
    def from_json(cls, obj: JSONCompatible) -> Self: ...
    @abstractmethod
    def to_json(self) -> JSONCompatible: ...
