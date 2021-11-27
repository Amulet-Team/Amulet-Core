from __future__ import annotations

from .anvil_2203 import (
    Anvil2203Interface,
)


class Anvil2529Interface(Anvil2203Interface):
    """
    Packed long arrays switched to a less dense format
    """

    def __init__(self):
        super().__init__()
        self._set_feature("long_array_format", "1.16")

    @staticmethod
    def minor_is_valid(key: int):
        return 2529 <= key < 2681


export = Anvil2529Interface
