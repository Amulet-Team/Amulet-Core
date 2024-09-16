from __future__ import annotations
from enum import IntEnum
from collections.abc import Mapping
from typing import TYPE_CHECKING

from amulet.game.abc import (
    DatabaseBlockData,
    BlockDataNumericalComponent,
    BlockSpec,
)
from amulet.game.translate import (
    BlockToUniversalTranslator,
    BlockFromUniversalTranslator,
)

if TYPE_CHECKING:
    from ._version import JavaGameVersion


class Waterloggable(IntEnum):
    No = 0
    Yes = 1
    Always = 2


class JavaBlockData(DatabaseBlockData, BlockDataNumericalComponent):
    def __init__(
        self,
        game_version: JavaGameVersion,
        specification: Mapping[str, Mapping[str, BlockSpec]],
        to_universal: Mapping[tuple[str, str], BlockToUniversalTranslator],
        from_universal: Mapping[tuple[str, str], BlockFromUniversalTranslator],
        numerical_map: Mapping[int, tuple[str, str]],
        waterloggable: Mapping[tuple[str, str], Waterloggable],
    ):
        super().__init__(game_version, specification, to_universal, from_universal)
        self._num_to_str = numerical_map
        self._str_to_num = {v: k for k, v in self._num_to_str.items()}
        self._waterloggable = waterloggable

    def __getstate__(self) -> dict:
        state = super().__getstate__()
        state["_num_to_str"] = self._num_to_str
        state["_waterloggable"] = self._waterloggable
        return state

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state)
        self._num_to_str = state["_num_to_str"]
        self._str_to_num = {v: k for k, v in self._num_to_str.items()}
        self._waterloggable = state["_waterloggable"]

    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        return self._num_to_str[numerical_id]

    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        return self._str_to_num[(namespace, base_name)]

    def waterloggable(self, namespace: str, base_name: str) -> Waterloggable:
        return self._waterloggable.get((namespace, base_name), Waterloggable.No)
