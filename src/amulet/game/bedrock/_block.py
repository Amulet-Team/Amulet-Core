from collections.abc import Mapping

from amulet.game.abc import (
    DatabaseBlockData,
    BlockDataNumericalComponent,
    GameVersion,
    BlockSpec,
)
from amulet.game.translate import (
    BlockToUniversalTranslator,
    BlockFromUniversalTranslator,
)


class BedrockBlockData(DatabaseBlockData, BlockDataNumericalComponent):
    def __init__(
        self,
        game_version: GameVersion,
        specification: Mapping[str, Mapping[str, BlockSpec]],
        to_universal: Mapping[tuple[str, str], BlockToUniversalTranslator],
        from_universal: Mapping[tuple[str, str], BlockFromUniversalTranslator],
        numerical_map: Mapping[int, tuple[str, str]],
    ):
        super().__init__(game_version, specification, to_universal, from_universal)
        self._num_to_str = numerical_map
        self._str_to_num = {v: k for k, v in self._num_to_str.items()}

    def __getstate__(self) -> dict:
        state = super().__getstate__()
        state["_num_to_str"] = self._num_to_str
        return state

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state)
        self._num_to_str = state["_num_to_str"]
        self._str_to_num = {v: k for k, v in self._num_to_str.items()}

    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        return self._num_to_str[numerical_id]

    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        return self._str_to_num[(namespace, base_name)]
