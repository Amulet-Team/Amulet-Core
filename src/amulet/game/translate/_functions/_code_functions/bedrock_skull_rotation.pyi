from .._state import DstData as DstData
from .._state import SrcData as SrcData
from .._state import StateData as StateData

def to_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
