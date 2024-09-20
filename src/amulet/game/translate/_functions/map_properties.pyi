from collections.abc import Mapping
from typing import Any, Self

from amulet.block import Block as Block
from amulet.block import PropertyValueType as PropertyValueType
from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict

from ._frozen import FrozenMapping as FrozenMapping
from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data
from .abc import immutable_from_snbt as immutable_from_snbt
from .abc import translation_function_from_json as translation_function_from_json

class MapProperties(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self,
        properties: Mapping[
            str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]
        ],
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
