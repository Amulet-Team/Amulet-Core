from .anvil_1519 import Anvil1519Interface as ParentInterface

class Anvil1901Interface(ParentInterface):
    """
    Block data in a section is optional
    """
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil1901Interface
