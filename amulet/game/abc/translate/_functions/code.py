from __future__ import annotations

from typing import Self, Literal
from collections.abc import Sequence

from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict, Data


class Code(AbstractBaseTranslationFunction):
    # Class variables
    Name = "code"
    _instances: dict[Code, Code] = {}

    # Instance variables
    _inputs: tuple[
        Literal["namespace"]
        | Literal["base_name"]
        | Literal["properties"]
        | Literal["nbt"]
        | Literal["location"]
    ]
    _outputs: tuple[
        Literal["output_name"]
        | Literal["output_type"]
        | Literal["new_properties"]
        | Literal["new_nbt"]
    ]
    _function_name: str

    def __new__(
        cls,
        inputs: Sequence[
            Literal["namespace"]
            | Literal["base_name"]
            | Literal["properties"]
            | Literal["nbt"]
            | Literal["location"]
        ],
        outputs: Sequence[
            Literal["output_name"]
            | Literal["output_type"]
            | Literal["new_properties"]
            | Literal["new_nbt"]
        ],
        function_name: str,
    ) -> Code:
        self = super().__new__(cls)
        self._inputs = tuple(inputs)
        self._outputs = tuple(outputs)
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
        return cls(options["input"], options["output"], options["function"])

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
