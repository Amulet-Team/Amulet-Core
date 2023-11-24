from __future__ import annotations

from collections.abc import Mapping

from .abc import AbstractBaseTranslationFunction
from ._frozen_map import FrozenMapping


class Code(AbstractBaseTranslationFunction):
    # Class variables
    Name = "code"

    # Instance variables
    _blocks: FrozenMapping[str, AbstractBaseTranslationFunction]

    def __init__(
            self, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ):

    # self._blocks = HashableMapping(blocks)
    # for block_name, func in self._blocks.items():
    #     if not isinstance(block_name, str):
    #         raise TypeError
    #     if not isinstance(func, AbstractBaseTranslationFunction):
    #         raise TypeError

    @classmethod
    def instance(
            cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> Code:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> Code:

    # if data.get("function") != "map_block_name":
    #     raise ValueError("Incorrect function data given.")
    # return cls.instance({
    #     block_name: from_json(function) for block_name, function in data["options"].items()
    # })

    def to_json(self):

    # return {
    #     "function": "map_block_name",
    #     "options": {
    #         block_name: func.to_json() for block_name, func in self._blocks.items()
    #     },
    # }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, Code):
            return NotImplemented
        return self._blocks == other._blocks
