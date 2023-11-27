from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping

from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONCompatible, JSONDict
from ._frozen import FrozenMapping


class WalkInputNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "walk_input_nbt"
    _instances: dict[Self, Self] = {}

    # Instance variables
    _blocks: FrozenMapping[str, AbstractBaseTranslationFunction]

    def __new__(cls) -> Self:
        self = super().__new__(cls)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        # if data.get("function") != "map_block_name":
        #     raise ValueError("Incorrect function data given.")
        # return cls({
        #     block_name: from_json(function) for block_name, function in data["options"].items()
        # })

    def to_json(self) -> JSONDict:
        # return {
        #     "function": "map_block_name",
        #     "options": {
        #         block_name: func.to_json() for block_name, func in self._blocks.items()
        #     },
        # }

    def __hash__(self) -> int:
        return hash(self._blocks)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, WalkInputNBT):
            return NotImplemented
        return self._blocks == other._blocks

    def run(self, *args, **kwargs):
        pass
