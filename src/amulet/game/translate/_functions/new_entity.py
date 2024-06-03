from __future__ import annotations

from typing import Self, Any

from amulet.entity import Entity
from .abc import AbstractBaseTranslationFunction, Data
from amulet.game.abc import JSONCompatible, JSONDict
from ._state import SrcData, StateData, DstData


class NewEntity(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_entity"
    _instances = {}

    # Instance variables
    _entity: tuple[str, str]

    def __init__(self, namespace: str, base_name: str) -> None:
        super().__init__()
        self._entity = (namespace, base_name)

    def __reduce__(self) -> Any:
        return NewEntity, (self._entity,)

    def _data(self) -> Data:
        return self._entity

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "new_entity"
        entity = data["options"]
        assert isinstance(entity, str)
        namespace, base_name = entity.split(":", 1)
        return cls(namespace, base_name)

    def to_json(self) -> JSONDict:
        return {"function": "new_entity", "options": ":".join(self._entity)}

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.cls = Entity
        dst.resource_id = self._entity
