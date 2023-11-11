from .anvil_2844 import Anvil2844Interface as ParentInterface
from amulet.api.chunk import StatusFormats as StatusFormats

class Anvil3463Interface(ParentInterface):
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil3463Interface
