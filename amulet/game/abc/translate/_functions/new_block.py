from __future__ import annotations

from typing import Self, Any
from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict


class NewBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_block"
    _instances: dict[Self, Self] = {}

    def __new__(cls, block: str) -> Self:
        self = super().__new__(cls)
        if not isinstance(block, str):
            raise TypeError
        self._block = block
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if data.get("function") != "new_block":
            raise ValueError("Incorrect function data given.")
        return cls(data["options"])

    def to_json(self) -> JSONDict:
        return {"function": "new_block", "options": self._block}

    def __hash__(self) -> int:
        return hash(self._block)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NewBlock):
            return NotImplemented
        return self._block == other._block

    def run(self, *args, **kwargs):
        raise NotImplementedError
