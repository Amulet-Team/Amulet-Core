from .anvil_1908 import Anvil1908Interface as ParentInterface
from amulet.api.chunk import StatusFormats as StatusFormats

class Anvil1912Interface(ParentInterface):
    """
    Changed status enum values
    """
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil1912Interface
