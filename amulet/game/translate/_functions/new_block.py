from __future__ import annotations

from typing import Self, Any
from amulet.block import Block
from .abc import AbstractBaseTranslationFunction, Data
from amulet.game.abc import JSONCompatible, JSONDict
from ._state import SrcData, StateData, DstData


class NewBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_block"
    _instances = {}

    # Instance variables
    _block: tuple[str, str]

    def __init__(self, namespace: str, base_name: str) -> None:
        super().__init__()
        self._block = (namespace, base_name)

    def __reduce__(self) -> Any:
        return NewBlock, (self._block[0], self._block[1])

    def _data(self) -> Data:
        return self._block

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "new_block"
        block = data["options"]
        assert isinstance(block, str)
        namespace, base_name = block.split(":", 1)
        return cls(namespace, base_name)

    def to_json(self) -> JSONDict:
        return {"function": "new_block", "options": ":".join(self._block)}

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.cls = Block
        dst.resource_id = self._block
