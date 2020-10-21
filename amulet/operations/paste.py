from __future__ import annotations

from typing import TYPE_CHECKING

from amulet.api.data_types import Dimension, BlockCoordinates, FloatTriplet
from amulet.api.block import Block, UniversalAirBlock

if TYPE_CHECKING:
    from amulet.api.world import ChunkWorld


def paste(
    dst: "ChunkWorld",
    dst_dimension: Dimension,
    src: "ChunkWorld",
    src_dimension: Dimension,
    location: BlockCoordinates,
    scale: FloatTriplet,
    rotation: FloatTriplet,
    copy_air=True,
    copy_water=True,
    copy_lava=True,
):
    for _ in paste_iter(
        dst,
        dst_dimension,
        src,
        src_dimension,
        location,
        scale,
        rotation,
        copy_air,
        copy_water,
        copy_lava,
    ):
        pass


def paste_iter(
    dst: "ChunkWorld",
    dst_dimension: Dimension,
    src: "ChunkWorld",
    src_dimension: Dimension,
    location: BlockCoordinates,
    scale: FloatTriplet,
    rotation: FloatTriplet,
    copy_air=True,
    copy_water=True,
    copy_lava=True,
):
    yield from dst.paste_iter(
        src,
        src_dimension,
        src.selection_bounds,
        dst_dimension,
        location,
        scale,
        rotation,
        True,
        True,
        (UniversalAirBlock,) * bool(not copy_air)
        + (Block("universal_minecraft", "water"),) * bool(not copy_water)
        + (Block("universal_minecraft", "lava"),) * bool(not copy_lava),
        True,
    )
