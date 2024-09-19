from __future__ import annotations

import types

from amulet.level.java.anvil._dimension import AnvilDimension, AnvilDimensionLayer
from amulet.level.java.anvil._region import AnvilRegion

from . import _dimension, _region, _sector_manager

__all__ = ["AnvilDimension", "AnvilDimensionLayer", "AnvilRegion", "RawChunkType"]
RawChunkType: types.GenericAlias  # value = dict[str, amulet_nbt.NamedTag]
