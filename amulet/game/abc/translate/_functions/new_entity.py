from __future__ import annotations

from typing import Self
from .abc import AbstractBaseTranslationFunction


class NewEntity(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_entity"
    _instances: dict[Self, Self] = {}

    # Instance variables
    _entity: str

    def __init__(self, entity: str):
        if not isinstance(entity, str):
            raise TypeError
        self._entity = entity

    @classmethod
    def instance(cls, entity: str) -> Self:
        self = cls(entity)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> Self:
        if data.get("function") != "new_entity":
            raise ValueError("Incorrect function data given.")
        return cls.instance(data["options"])

    def to_json(self) -> dict:
        return {"function": "new_entity", "options": self._entity}

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._entity)

    def __eq__(self, other):
        if not isinstance(other, NewEntity):
            return NotImplemented
        return self._entity == other._entity
