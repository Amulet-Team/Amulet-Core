from amulet.api.data_types import Dimension as Dimension, OperationReturnType as OperationReturnType
from amulet.api.level import BaseLevel as BaseLevel
from amulet.block import Block as Block
from amulet.selection import SelectionGroup as SelectionGroup

def fill(world: BaseLevel, dimension: Dimension, target_box: SelectionGroup, fill_block: Block) -> OperationReturnType: ...
