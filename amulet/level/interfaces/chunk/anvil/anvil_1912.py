from __future__ import annotations

from .anvil_1908 import Anvil1908Interface as ParentInterface
from amulet.api.chunk import StatusFormats


class Anvil1912Interface(ParentInterface):
    """
    Changed status enum values
    """


export = Anvil1912Interface
