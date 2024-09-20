from collections.abc import Mapping
from typing import Any, Self

from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict

from ._frozen import FrozenMapping as FrozenMapping
from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data
from .abc import follow_nbt_path as follow_nbt_path
from .abc import translation_function_from_json as translation_function_from_json

class MapNBT(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self,
        cases: Mapping[str, AbstractBaseTranslationFunction],
        default: AbstractBaseTranslationFunction | None,
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
