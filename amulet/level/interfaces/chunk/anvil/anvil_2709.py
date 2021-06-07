from __future__ import annotations

from .anvil_2529 import (
    Anvil2529Interface,
)
from .feature_enum import HeightState, BiomeState


class Anvil2709Interface(Anvil2529Interface):
    def __init__(self):
        super().__init__()
        self._set_feature("height_state", HeightState.Variable1_17)
        self._set_feature("biomes", BiomeState.IANx64)

    @staticmethod
    def minor_is_valid(key: int):
        return 2709 <= key < 2800


export = Anvil2709Interface
