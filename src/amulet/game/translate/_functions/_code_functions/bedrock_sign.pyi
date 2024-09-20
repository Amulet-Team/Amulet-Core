from _typeshed import Incomplete

from .._state import DstData as DstData
from .._state import SrcData as SrcData
from .._state import StateData as StateData
from ._text import ExtendedBedrockSectionParser as ExtendedBedrockSectionParser
from ._text import RawTextComponent as RawTextComponent

BedrockFrontText: Incomplete
BedrockBackText: Incomplete

def to_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
def from_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
def to_universal_120(src: SrcData, state: StateData, dst: DstData) -> None: ...
def from_universal_120(src: SrcData, state: StateData, dst: DstData) -> None: ...
