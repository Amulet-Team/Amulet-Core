from .anvil_1912 import Anvil1912Interface as ParentInterface

class Anvil1934Interface(ParentInterface):
    """
    Made lighting optional
    """
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil1934Interface
