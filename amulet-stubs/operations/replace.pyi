from _typeshed import Incomplete
from amulet.api.data_types import Dimension as Dimension
from amulet.api.level import BaseLevel as BaseLevel
from amulet.block import Block as Block
from amulet.selection import SelectionGroup as SelectionGroup

log: Incomplete

def replace(world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict): ...
