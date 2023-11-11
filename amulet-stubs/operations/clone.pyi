from amulet.api.data_types import Dimension as Dimension
from amulet.api.level import BaseLevel as BaseLevel
from amulet.selection import SelectionGroup as SelectionGroup

def clone(world: BaseLevel, dimension: Dimension, selection: SelectionGroup, target: dict): ...
