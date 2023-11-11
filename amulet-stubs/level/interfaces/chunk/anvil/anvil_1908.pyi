from .anvil_1901 import Anvil1901Interface as ParentInterface

class Anvil1908Interface(ParentInterface):
    """
    Changed height keys again again
    """
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil1908Interface
