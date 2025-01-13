from __future__ import annotations

import typing

from amulet.level.java.anvil.dimension import AnvilDimension, AnvilDimensionLayer
from amulet.level.java.anvil.region import AnvilRegion

from . import dimension, region

__all__ = [
    "AnvilDimension",
    "AnvilDimensionLayer",
    "AnvilRegion",
    "RawChunkType",
    "dimension",
    "region",
]
RawChunkType: typing.TypeAlias = dict[str, amulet_nbt.NamedTag]
