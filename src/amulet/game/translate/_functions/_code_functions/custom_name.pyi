from typing import Callable

from _typeshed import Incomplete
from amulet_nbt import StringTag

from .._state import DstData as DstData
from .._state import SrcData as SrcData
from .._state import StateData as StateData
from ._text import BedrockSectionParser as BedrockSectionParser
from ._text import ExtendedBedrockSectionParser as ExtendedBedrockSectionParser
from ._text import JavaSectionParser as JavaSectionParser
from ._text import RawTextComponent as RawTextComponent

JavaSectionText: Incomplete
JavaRawText: Incomplete
BedrockSectionText: Incomplete
BedrockExtendedSectionText: Incomplete

def get_custom_name(src: SrcData, dst: DstData, key: str) -> None: ...
def java_section_to_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
def java_raw_to_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
def bedrock_to_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
def bedrock_extended_to_universal(
    src: SrcData, state: StateData, dst: DstData
) -> None: ...
def set_custom_name(
    src: SrcData,
    dst: DstData,
    target: str,
    component_to_raw: Callable[[RawTextComponent], StringTag],
) -> None: ...
def java_section_from_universal(
    src: SrcData, state: StateData, dst: DstData
) -> None: ...
def java_raw_from_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
def bedrock_from_universal(src: SrcData, state: StateData, dst: DstData) -> None: ...
def bedrock_extended_from_universal(
    src: SrcData, state: StateData, dst: DstData
) -> None: ...
