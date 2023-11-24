from __future__ import annotations

from typing import Self
from collections.abc import Sequence

from .abc import AbstractBaseTranslationFunction, from_json


class TranslationFunctionSequence(AbstractBaseTranslationFunction):
    # Class variables
    Name = "sequence"
    _instances: dict[Self, Self] = {}

    # Instance variables
    _functions: tuple[AbstractBaseTranslationFunction]

    def __init__(self, functions: Sequence[AbstractBaseTranslationFunction]):
        self._functions = tuple(functions)
        if not all(
            isinstance(inst, AbstractBaseTranslationFunction)
            for inst in self._functions
        ):
            raise TypeError

    @classmethod
    def instance(
        cls, functions: Sequence[AbstractBaseTranslationFunction]
    ) -> Self:
        self = cls(functions)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: list) -> Self:
        parsed = []
        for func in data:
            parsed.append(from_json(func))

        return cls.instance(parsed)

    def to_json(self) -> list:
        return [func.to_json() for func in self._functions]

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._functions)

    def __eq__(self, other):
        if not isinstance(other, TranslationFunctionSequence):
            return NotImplemented
        return self._functions == other._functions
