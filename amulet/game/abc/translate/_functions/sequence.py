from __future__ import annotations

from typing import Self, Any
from collections.abc import Sequence

from .abc import (
    AbstractBaseTranslationFunction,
    translation_function_from_json,
    JSONCompatible,
    JSONList,
    Data,
)
from ._state import SrcData, StateData, DstData


class TranslationFunctionSequence(AbstractBaseTranslationFunction):
    # Class variables
    Name = "sequence"
    _instances: dict[TranslationFunctionSequence, TranslationFunctionSequence] = {}

    # Instance variables
    _functions: tuple[AbstractBaseTranslationFunction, ...]

    def __new__(
        cls, functions: Sequence[AbstractBaseTranslationFunction]
    ) -> TranslationFunctionSequence:
        self = super().__new__(cls)
        self._functions = tuple(functions)
        if not all(
            isinstance(inst, AbstractBaseTranslationFunction)
            for inst in self._functions
        ):
            raise TypeError
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._functions

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, Sequence)
        return cls([translation_function_from_json(func) for func in data])

    def to_json(self) -> JSONList:
        return [func.to_json() for func in self._functions]

    def __bool__(self) -> bool:
        return bool(self._functions)

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        for func in self._functions:
            func.run(src, state, dst)
