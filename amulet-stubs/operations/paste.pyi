from amulet.api.data_types import BlockCoordinates as BlockCoordinates, Dimension as Dimension, FloatTriplet as FloatTriplet
from amulet.api.level import BaseLevel as BaseLevel
from amulet.block import Block as Block, UniversalAirLikeBlocks as UniversalAirLikeBlocks

def paste(dst: BaseLevel, dst_dimension: Dimension, src: BaseLevel, src_dimension: Dimension, location: BlockCoordinates, scale: FloatTriplet, rotation: FloatTriplet, copy_air: bool = ..., copy_water: bool = ..., copy_lava: bool = ...): ...
def paste_iter(dst: BaseLevel, dst_dimension: Dimension, src: BaseLevel, src_dimension: Dimension, location: BlockCoordinates, scale: FloatTriplet, rotation: FloatTriplet, copy_air: bool = ..., copy_water: bool = ..., copy_lava: bool = ...): ...
