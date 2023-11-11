from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import Dimension as Dimension
from amulet.api.level import BaseLevel as BaseLevel
from amulet.selection import SelectionGroup as SelectionGroup

def delete_chunk(world: BaseLevel, dimension: Dimension, source_box: SelectionGroup, load_original: bool = ...): ...
