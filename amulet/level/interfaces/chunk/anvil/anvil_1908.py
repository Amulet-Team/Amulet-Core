from __future__ import annotations

from .anvil_1901 import Anvil1901Interface as ParentInterface


class Anvil1908Interface(ParentInterface):
    """
    Changed height keys again again
    """

    @staticmethod
    def minor_is_valid(key: int):
        return 1908 <= key < 1912


export = Anvil1908Interface
