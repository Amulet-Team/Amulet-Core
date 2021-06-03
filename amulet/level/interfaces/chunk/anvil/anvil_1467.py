from __future__ import annotations

from .anvil_1466 import (
    Anvil1466Interface,
)
from .feature_enum import BiomeState


class Anvil1467Interface(Anvil1466Interface):
    def __init__(self):
        super().__init__()
        self._set_feature("biomes", BiomeState.IA256)

    @staticmethod
    def minor_is_valid(key: int):
        return 1467 <= key < 1484


export = Anvil1467Interface
