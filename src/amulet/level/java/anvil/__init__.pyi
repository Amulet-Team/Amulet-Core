from __future__ import annotations

import typing

import amulet_nbt
from amulet.level.java.anvil.dimension import AnvilDimension, AnvilDimensionLayer
from amulet.level.java.anvil.region import AnvilRegion, RegionDoesNotExist

from . import dimension, region

__all__ = [
    "AnvilDimension",
    "AnvilDimensionLayer",
    "AnvilRegion",
    "RawChunkType",
    "RegionDoesNotExist",
    "dimension",
    "region",
]
RawChunkType: typing.TypeAlias = dict[str, amulet_nbt.NamedTag]
