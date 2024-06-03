from __future__ import annotations

from typing import Self, Any, TypeVar, Callable
from collections.abc import Sequence

from .abc import AbstractBaseTranslationFunction, Data
from amulet.game.abc import JSONCompatible, JSONDict
from ._state import SrcData, StateData, DstData

from ._code_functions.banner_pattern import (
    to_universal as banner_pattern_2u,
    from_universal as banner_pattern_fu,
)
from ._code_functions.bedrock_chest_connection import (
    bedrock_chest_connection_self,
    bedrock_chest_connection_self_120,
    bedrock_chest_connection_other_left,
    bedrock_chest_connection_other_left_120,
    bedrock_chest_connection_other_right,
    bedrock_chest_connection_other_right_120,
    from_universal as bedrock_chest_fu,
)
from ._code_functions.custom_name import (
    bedrock_extended_to_universal as bedrock_custom_name_2u,
    bedrock_extended_from_universal as bedrock_custom_name_fu,
)
from ._code_functions.bedrock_moving_block_pos import (
    to_universal as bedrock_moving_block_pos_2u,
    from_universal as bedrock_moving_block_pos_fu,
)
from ._code_functions.bedrock_sign import (
    to_universal as bedrock_sign_2u,
    from_universal as bedrock_sign_fu,
    to_universal_120 as bedrock_sign_2u_120,
    from_universal_120 as bedrock_sign_fu_120,
)
from ._code_functions.bedrock_skull_rotation import (
    to_universal as bedrock_skull_rotation_2u,
)


T = TypeVar("T")


def check_list(l: list[Any], t: type[T]) -> list[T]:
    assert all(isinstance(el, t) for el in l)
    return l


FunctionLUT: dict[str, Callable[[SrcData, StateData, DstData], None]] = {
    "banner_pattern_2u": banner_pattern_2u,
    "banner_pattern_fu": banner_pattern_fu,
    "bedrock_chest_connection_other_left": bedrock_chest_connection_other_left,
    "bedrock_chest_connection_other_left_120": bedrock_chest_connection_other_left_120,
    "bedrock_chest_connection_other_right": bedrock_chest_connection_other_right,
    "bedrock_chest_connection_other_right_120": bedrock_chest_connection_other_right_120,
    "bedrock_chest_connection_self": bedrock_chest_connection_self,
    "bedrock_chest_connection_self_120": bedrock_chest_connection_self_120,
    "bedrock_chest_fu": bedrock_chest_fu,
    "bedrock_cmd_custom_name_2u": bedrock_custom_name_2u,
    "bedrock_cmd_custom_name_fu": bedrock_custom_name_fu,
    "bedrock_moving_block_pos_2u": bedrock_moving_block_pos_2u,
    "bedrock_moving_block_pos_fu": bedrock_moving_block_pos_fu,
    "bedrock_sign_2u": bedrock_sign_2u,
    "bedrock_sign_2u_120": bedrock_sign_2u_120,
    "bedrock_sign_fu": bedrock_sign_fu,
    "bedrock_sign_fu_120": bedrock_sign_fu_120,
    "bedrock_skull_rotation_2u": bedrock_skull_rotation_2u,
}


class Code(AbstractBaseTranslationFunction):
    # Class variables
    Name = "code"
    _instances = {}

    # Instance variables
    _inputs: tuple[str, ...]
    _outputs: tuple[str, ...]
    _function_name: str

    def __init__(
        self,
        inputs: Sequence[str],
        outputs: Sequence[str],
        function_name: str,
    ) -> None:
        super().__init__()
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

    def __reduce__(self) -> Any:
        return Code, (self._inputs, self._outputs, self._function_name)

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
        assert function in FunctionLUT, function
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

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.cacheable = False
        FunctionLUT[self._function_name](src, state, dst)
