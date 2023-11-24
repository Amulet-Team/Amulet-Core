from __future__ import annotations

from collections.abc import Sequence

from .abc import AbstractBaseTranslationFunction


class TranslationFunctionSequence(AbstractBaseTranslationFunction):
    # class variables
    Name = "sequence"

    # instance variables
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
    ) -> TranslationFunctionSequence:
        self = cls(functions)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: list) -> TranslationFunctionSequence:
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
