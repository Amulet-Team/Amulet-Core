from __future__ import annotations

from typing import Self, Any
from collections.abc import Sequence

from .abc import AbstractBaseTranslationFunction, from_json, JSONCompatible, JSONList


class TranslationFunctionSequence(AbstractBaseTranslationFunction):
    # Class variables
    Name = "sequence"
    _instances: dict[Self, Self] = {}

    # Instance variables
    _functions: tuple[AbstractBaseTranslationFunction]

    def __new__(cls, functions: Sequence[AbstractBaseTranslationFunction]) -> Self:
        self = super().__new__(cls)
        self._functions = tuple(functions)
        if not all(
            isinstance(inst, AbstractBaseTranslationFunction)
            for inst in self._functions
        ):
            raise TypeError
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if not isinstance(data, Sequence):
            raise TypeError
        return cls([from_json(func) for func in data])

    def to_json(self) -> JSONList:
        return [func.to_json() for func in self._functions]

    def __hash__(self) -> int:
        return hash(self._functions)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TranslationFunctionSequence):
            return NotImplemented
        return self._functions == other._functions

    def run(self, *args, **kwargs):
        raise NotImplementedError
