from .anvil_1484 import Anvil1484Interface as ParentInterface

class Anvil1503Interface(ParentInterface):
    """
    Changed height keys again
    """
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil1503Interface
