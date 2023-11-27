from __future__ import annotations

from typing import Self, Any
from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict


class NewEntity(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_entity"
    _instances: dict[Self, Self] = {}

    def __new__(cls, entity: str) -> Self:
        self = super().__new__(cls)
        if not isinstance(entity, str):
            raise TypeError
        self._entity = entity
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if data.get("function") != "new_entity":
            raise ValueError("Incorrect function data given.")
        return cls(data["options"])

    def to_json(self) -> JSONDict:
        return {"function": "new_entity", "options": self._entity}

    def __hash__(self) -> int:
        return hash(self._entity)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NewEntity):
            return NotImplemented
        return self._entity == other._entity

    def run(self, *args, **kwargs):
        raise NotImplementedError
