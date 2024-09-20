from collections.abc import Sequence
from typing import Any, Callable, Self, TypeVar

from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict

from ._code_functions.bedrock_chest_connection import (
    bedrock_chest_connection_other_left as bedrock_chest_connection_other_left,
)
from ._code_functions.bedrock_chest_connection import (
    bedrock_chest_connection_other_left_120 as bedrock_chest_connection_other_left_120,
)
from ._code_functions.bedrock_chest_connection import (
    bedrock_chest_connection_other_right as bedrock_chest_connection_other_right,
)
from ._code_functions.bedrock_chest_connection import (
    bedrock_chest_connection_other_right_120 as bedrock_chest_connection_other_right_120,
)
from ._code_functions.bedrock_chest_connection import (
    bedrock_chest_connection_self as bedrock_chest_connection_self,
)
from ._code_functions.bedrock_chest_connection import (
    bedrock_chest_connection_self_120 as bedrock_chest_connection_self_120,
)
from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data

T = TypeVar("T")

def check_list(l: list[Any], t: type[T]) -> list[T]: ...

FunctionLUT: dict[str, Callable[[SrcData, StateData, DstData], None]]

class Code(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self, inputs: Sequence[str], outputs: Sequence[str], function_name: str
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
