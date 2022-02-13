from __future__ import annotations

from .anvil_2529 import (
    Anvil2529Interface,
)


class Anvil2681Interface(Anvil2529Interface):
    """
    Entities moved to a different storage layer
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 2681 <= key < 2709


export = Anvil2681Interface
