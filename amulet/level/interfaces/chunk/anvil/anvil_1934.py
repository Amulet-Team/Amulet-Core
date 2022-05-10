from __future__ import annotations

from .anvil_1912 import Anvil1912Interface as ParentInterface


class Anvil1934Interface(ParentInterface):
    """
    Made lighting optional
    """

    def __init__(self):
        super().__init__()
        self._set_feature("light_optional", "true")

    @staticmethod
    def minor_is_valid(key: int):
        return 1934 <= key < 2203


export = Anvil1934Interface
