from collections.abc import Mapping
from enum import IntEnum

from amulet.game.abc import BlockDataNumericalComponent as BlockDataNumericalComponent
from amulet.game.abc import BlockSpec as BlockSpec
from amulet.game.abc import DatabaseBlockData as DatabaseBlockData
from amulet.game.translate import (
    BlockFromUniversalTranslator as BlockFromUniversalTranslator,
)
from amulet.game.translate import (
    BlockToUniversalTranslator as BlockToUniversalTranslator,
)

from ._version import JavaGameVersion as JavaGameVersion

class Waterloggable(IntEnum):
    No: int
    Yes: int
    Always: int

class JavaBlockData(DatabaseBlockData, BlockDataNumericalComponent):
    def __init__(
        self,
        game_version: JavaGameVersion,
        specification: Mapping[str, Mapping[str, BlockSpec]],
        to_universal: Mapping[tuple[str, str], BlockToUniversalTranslator],
        from_universal: Mapping[tuple[str, str], BlockFromUniversalTranslator],
        numerical_map: Mapping[int, tuple[str, str]],
        waterloggable: Mapping[tuple[str, str], Waterloggable],
    ) -> None: ...
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]: ...
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int: ...
    def waterloggable(self, namespace: str, base_name: str) -> Waterloggable: ...
