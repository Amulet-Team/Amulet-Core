from __future__ import annotations

from .anvil_2529 import (
    Anvil2529Interface,
)


class Anvil2709Interface(Anvil2529Interface):
    """
    Made height bit depth variable to store increased heights
    Made the biome array size variable to handle the increased height
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 2709 <= key < 2800


export = Anvil2709Interface
