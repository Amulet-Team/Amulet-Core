from __future__ import annotations

from .anvil_2203 import Anvil2203Interface as ParentInterface


class Anvil2529Interface(ParentInterface):
    """
    Packed long arrays switched to a less dense format
    Before the long array was just a bit stream but it is now separate longs. The upper bits are unused in some cases.
    """

    LongArrayDense = False

    @staticmethod
    def minor_is_valid(key: int):
        return 2529 <= key < 2681


export = Anvil2529Interface
