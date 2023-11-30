from __future__ import annotations

from typing import Self, Any, TypeVar
from collections.abc import Sequence

from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict, Data


T = TypeVar("T")


def check_list(l: list[Any], t: type[T]) -> list[T]:
    assert all(isinstance(el, t) for el in l)
    return l


class Code(AbstractBaseTranslationFunction):
    # Class variables
    Name = "code"
    _instances: dict[Code, Code] = {}

    # Instance variables
    _inputs: tuple[str, ...]
    _outputs: tuple[str, ...]
    _function_name: str

    def __new__(
        cls,
        inputs: Sequence[str],
        outputs: Sequence[str],
        function_name: str,
    ) -> Code:
        self = super().__new__(cls)
        self._inputs = tuple(inputs)
        assert all(
            el
            in {
                "namespace",
                "base_name",
                "properties",
                "nbt",
                "location",
            }
            for el in self._inputs
        )
        self._outputs = tuple(outputs)
        assert all(
            el in {"output_name", "output_type", "new_properties", "new_nbt"}
            for el in self._outputs
        )
        self._function_name = function_name
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._inputs, self._outputs, self._function_name

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "code"
        options = data["options"]
        assert isinstance(options, dict)
        raw_inputs = options["input"]
        assert isinstance(raw_inputs, list)
        inputs = check_list(raw_inputs, str)
        raw_outputs = options["output"]
        assert isinstance(raw_outputs, list)
        outputs = check_list(raw_outputs, str)
        function = options["function"]
        assert isinstance(function, str)
        return cls(inputs, outputs, function)

    def to_json(self) -> JSONDict:
        return {
            "function": "code",
            "options": {
                "input": list(self._inputs),
                "output": list(self._outputs),
                "function": self._function_name,
            },
        }

    def run(self, *args, **kwargs):
        pass
