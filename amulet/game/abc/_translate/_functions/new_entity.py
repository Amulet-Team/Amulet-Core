from __future__ import annotations

from .abc import AbstractBaseTranslationFunction


class NewEntity(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_entity"

    # instance variables
    _entity: str

    def __init__(self, entity: str):
        if not isinstance(entity, str):
            raise TypeError
        self._entity = entity

    @classmethod
    def instance(cls, entity: str) -> NewEntity:
        self = cls(entity)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> NewEntity:
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
