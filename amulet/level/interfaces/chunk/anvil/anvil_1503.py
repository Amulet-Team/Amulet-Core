from __future__ import annotations

from .anvil_1484 import Anvil1484Interface as ParentInterface


class Anvil1503Interface(ParentInterface):
    """
    Changed height keys again
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 1503 <= key < 1519


export = Anvil1503Interface
