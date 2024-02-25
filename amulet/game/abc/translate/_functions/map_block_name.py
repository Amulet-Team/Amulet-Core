from __future__ import annotations

from typing import Self
from collections.abc import Mapping

from amulet.block import Block
from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    translation_function_from_json,
    Data,
)
from ._frozen import FrozenMapping
from ._state import SrcData, StateData, DstData


class MapBlockName(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_block_name"
    _instances: dict[MapBlockName, MapBlockName] = {}

    # Instance variables
    _blocks: FrozenMapping[tuple[str, str], AbstractBaseTranslationFunction]

    def __new__(
        cls, blocks: Mapping[tuple[str, str], AbstractBaseTranslationFunction]
    ) -> MapBlockName:
        self = super().__new__(cls)
        self._blocks = FrozenMapping[tuple[str, str], AbstractBaseTranslationFunction](
            blocks
        )
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._blocks

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "map_block_name"
        blocks = {}
        options = data["options"]
        assert isinstance(options, dict)
        for block_name, function in options.items():
            assert isinstance(block_name, str)
            namespace, base_name = block_name.split(":", 1)
            blocks[(namespace, base_name)] = translation_function_from_json(function)
        return cls(blocks)

    def to_json(self) -> JSONDict:
        return {
            "function": "map_block_name",
            "options": {
                ":".join(block_name): func.to_json()
                for block_name, func in self._blocks.items()
            },
        }

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        block = src.block
        assert isinstance(block, Block)
        func = self._blocks.get((block.namespace, block.base_name))
        if func is not None:
            func.run(src, state, dst)
