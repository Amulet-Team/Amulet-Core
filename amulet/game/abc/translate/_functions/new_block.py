from __future__ import annotations

from typing import Self
from .abc import AbstractBaseTranslationFunction


class NewBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_block"
    _instances: dict[Self, Self] = {}

    # Instance variables
    _block: str

    def __init__(self, block: str):
        if not isinstance(block, str):
            raise TypeError
        self._block = block

    @classmethod
    def instance(cls, block: str) -> Self:
        self = cls(block)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> Self:
        if data.get("function") != "new_block":
            raise ValueError("Incorrect function data given.")
        return cls.instance(data["options"])

    def to_json(self) -> dict:
        return {"function": "new_block", "options": self._block}

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._block)

    def __eq__(self, other):
        if not isinstance(other, NewBlock):
            return NotImplemented
        return self._block == other._block
