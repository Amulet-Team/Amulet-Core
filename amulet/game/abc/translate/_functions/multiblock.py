from __future__ import annotations

from typing import Sequence, Self

from amulet.api.data_types import BlockCoordinates
from .abc import AbstractBaseTranslationFunction


class MultiBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "multiblock"
    _instances: dict[Self, Self] = {}

    # Instance variables
    _blocks: tuple[tuple[BlockCoordinates, AbstractBaseTranslationFunction], ...]

    def __init__(
        self, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ):
        self._blocks = tuple(blocks)
        for coords, func in self._blocks:
            if (
                not isinstance(coords, tuple)
                and len(coords) == 3
                and all(isinstance(v, int) for v in coords)
            ):
                raise TypeError
            if not isinstance(func, AbstractBaseTranslationFunction):
                raise TypeError

    @classmethod
    def instance(
        cls, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ) -> Self:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> Self:
        if data.get("function") != "multiblock":
            raise ValueError("Incorrect function data given.")
        return cls.instance(
            [(block["coords"], block["functions"]) for block in data["options"]]
        )

    def to_json(self):
        return {
            "function": "multiblock",
            "options": [
                {"coords": list(coords), "functions": func.to_json()}
                for coords, func in self._blocks
            ],
        }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, MultiBlock):
            return NotImplemented
        return self._blocks == other._blocks
