from .anvil_1467 import Anvil1467Interface as ParentInterface

class Anvil1484Interface(ParentInterface):
    """
    Changed height keys
    """
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil1484Interface
