from __future__ import annotations

from typing import Self, Any
from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict, Data


class NewBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_block"
    _instances: dict[NewBlock, NewBlock] = {}

    def __new__(cls, block: str) -> NewBlock:
        self = super().__new__(cls)
        assert isinstance(block, str)
        self._block = block
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._block

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "new_block"
        return cls(data["options"])

    def to_json(self) -> JSONDict:
        return {"function": "new_block", "options": self._block}

    def run(self, *args, **kwargs):
        raise NotImplementedError
