from .anvil_2203 import Anvil2203Interface as ParentInterface

class Anvil2529Interface(ParentInterface):
    """
    Packed long arrays switched to a less dense format
    Before the long array was just a bit stream but it is now separate longs. The upper bits are unused in some cases.
    """
    LongArrayDense: bool
    @staticmethod
    def minor_is_valid(key: int): ...
export = Anvil2529Interface
