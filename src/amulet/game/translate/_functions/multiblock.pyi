from typing import Any, Self, Sequence

from amulet.data_types import BlockCoordinates as BlockCoordinates
from amulet.errors import ChunkLoadError as ChunkLoadError
from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict

from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import SrcDataExtra as SrcDataExtra
from ._state import StateData as StateData
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data
from .abc import translation_function_from_json as translation_function_from_json

class MultiBlock(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
