from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    from_json,
    Data,
)
from ._frozen import FrozenMapping


class MapBlockName(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_block_name"
    _instances: dict[MapBlockName, MapBlockName] = {}

    def __new__(
        cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> MapBlockName:
        self = super().__new__(cls)
        self._blocks = FrozenMapping[str, AbstractBaseTranslationFunction](blocks)
        for block_name, func in self._blocks.items():
            assert isinstance(block_name, str)
            assert isinstance(func, AbstractBaseTranslationFunction)
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._blocks

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "map_block_name"
        return cls(
            {
                block_name: from_json(function)
                for block_name, function in data["options"].items()
            }
        )

    def to_json(self) -> JSONDict:
        return {
            "function": "map_block_name",
            "options": {
                block_name: func.to_json() for block_name, func in self._blocks.items()
            },
        }

    def run(self, *args, **kwargs):
        pass
