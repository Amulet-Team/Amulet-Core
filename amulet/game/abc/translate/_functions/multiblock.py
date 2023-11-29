from __future__ import annotations

from typing import Sequence, Self, Any

from amulet.api.data_types import BlockCoordinates
from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    Data,
    from_json,
)


class MultiBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "multiblock"
    _instances: dict[MultiBlock, MultiBlock] = {}

    _blocks: tuple[tuple[BlockCoordinates, AbstractBaseTranslationFunction], ...]

    def __new__(
        cls, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ) -> MultiBlock:
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
            assert isinstance(func, AbstractBaseTranslationFunction)
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._blocks

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "multiblock"
        options = data["options"]
        assert isinstance(options, list)
        blocks: list[tuple[BlockCoordinates, AbstractBaseTranslationFunction]] = []
        for block in options:
            assert isinstance(block, dict)
            raw_coords = block["coords"]
            assert isinstance(raw_coords, list)
            coords = (raw_coords[0], raw_coords[1], raw_coords[2])
            function = from_json(block["functions"])
            blocks.append((coords, function))
        return cls(blocks)

    def to_json(self) -> JSONDict:
        return {
            "function": "multiblock",
            "options": [
                {"coords": list(coords), "functions": func.to_json()}
                for coords, func in self._blocks
            ],
        }

    def run(self, *args, **kwargs):
        pass
