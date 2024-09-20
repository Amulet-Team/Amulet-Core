from typing import Any, Self

from amulet.entity import Entity as Entity
from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict

from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data

class NewEntity(AbstractBaseTranslationFunction):
    Name: str
    def __init__(self, namespace: str, base_name: str) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
