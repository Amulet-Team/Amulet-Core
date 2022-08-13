from __future__ import annotations

from .anvil_1519 import Anvil1519Interface as ParentInterface


class Anvil1901Interface(ParentInterface):
    """
    Block data in a section is optional
    """

    def __init__(self):
        super().__init__()
        self._unregister_post_encoder(self._post_encode_sections)

    @staticmethod
    def minor_is_valid(key: int):
        return 1901 <= key < 1908


export = Anvil1901Interface
