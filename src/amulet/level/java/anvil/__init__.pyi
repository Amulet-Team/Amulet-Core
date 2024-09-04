from __future__ import annotations
from amulet.level.java.anvil._dimension import AnvilDimension
from amulet.level.java.anvil._dimension import AnvilDimensionLayer
from amulet.level.java.anvil._region import AnvilRegion
import types
from . import _dimension
from . import _region
from . import _sector_manager

__all__ = ["AnvilDimension", "AnvilDimensionLayer", "AnvilRegion", "RawChunkType"]
RawChunkType: types.GenericAlias  # value = dict[str, amulet_nbt.NamedTag]
