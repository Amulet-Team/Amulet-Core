from __future__ import annotations

from .anvil_2681 import (
    Anvil2681Interface as ParentInterface,
)


class Anvil2709Interface(ParentInterface):
    """
    Made height bit depth variable to store increased heights
    Made the biome array size variable to handle the increased height
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 2709 <= key < 2800


export = Anvil2709Interface
