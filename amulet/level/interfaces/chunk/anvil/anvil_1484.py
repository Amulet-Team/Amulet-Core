from __future__ import annotations

from .anvil_1467 import Anvil1467Interface as ParentInterface


class Anvil1484Interface(ParentInterface):
    """
    Changed height keys
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 1484 <= key < 1503


export = Anvil1484Interface
