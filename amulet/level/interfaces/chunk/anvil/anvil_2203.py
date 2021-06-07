from __future__ import annotations

from .anvil_1934 import (
    Anvil1934Interface,
)
from .feature_enum import BiomeState


class Anvil2203Interface(Anvil1934Interface):
    def __init__(self):
        super().__init__()
        self._set_feature("biomes", BiomeState.IA1024)  # optional

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529


export = Anvil2203Interface
