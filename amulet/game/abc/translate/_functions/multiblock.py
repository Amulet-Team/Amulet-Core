from __future__ import annotations

from typing import Sequence, Self, Any

from amulet.api.data_types import BlockCoordinates
from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict


class MultiBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "multiblock"
    _instances: dict[Self, Self] = {}

    def __new__(
        cls, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ) -> Self:
        self = super().__new__(cls)
        self._blocks = tuple[
            tuple[BlockCoordinates, AbstractBaseTranslationFunction], ...
        ](blocks)
        for coords, func in self._blocks:
            if (
                not isinstance(coords, tuple)
                and len(coords) == 3
                and all(isinstance(v, int) for v in coords)
            ):
                raise TypeError
            if not isinstance(func, AbstractBaseTranslationFunction):
                raise TypeError
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if data.get("function") != "multiblock":
            raise ValueError("Incorrect function data given.")
        return cls([(block["coords"], block["functions"]) for block in data["options"]])

    def to_json(self) -> JSONDict:
        return {
            "function": "multiblock",
            "options": [
                {"coords": list(coords), "functions": func.to_json()}
                for coords, func in self._blocks
            ],
        }

    def __hash__(self) -> int:
        return hash(self._blocks)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MultiBlock):
            return NotImplemented
        return self._blocks == other._blocks

    def run(self, *args, **kwargs):
        pass
