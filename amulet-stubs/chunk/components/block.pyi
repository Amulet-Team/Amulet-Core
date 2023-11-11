from _typeshed import Incomplete
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer as SubChunkArrayContainer
from amulet.palette import BlockPalette as BlockPalette
from amulet.version import VersionRange as VersionRange
from numpy.typing import ArrayLike as ArrayLike
from typing import Iterable, Union

class BlockComponent:
    __block_palette: Incomplete
    __blocks: Incomplete
    def __init__(self, version_range: VersionRange, array_shape: tuple[int, int, int], default_array: Union[int, ArrayLike]) -> None: ...
    @property
    def block(self) -> SubChunkArrayContainer: ...
    @block.setter
    def block(self, sections: Iterable[int, ArrayLike]): ...
    @property
    def block_palette(self): ...
