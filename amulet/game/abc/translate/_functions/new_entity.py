from __future__ import annotations

from typing import Self, Any
from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict, Data


class NewEntity(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_entity"
    _instances: dict[NewEntity, NewEntity] = {}

    def __new__(cls, entity: str) -> NewEntity:
        self = super().__new__(cls)
        assert isinstance(entity, str)
        self._entity = entity
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._entity

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "new_entity"
        return cls(data["options"])

    def to_json(self) -> JSONDict:
        return {"function": "new_entity", "options": self._entity}

    def run(self, *args, **kwargs):
        raise NotImplementedError
