from __future__ import annotations

from typing import TYPE_CHECKING

from amulet.api.data_types import Dimension, BlockCoordinates, FloatTriplet
from amulet.api.block import Block

if TYPE_CHECKING:
    from amulet.api.world import ChunkWorld, Structure


def paste(
    world: "ChunkWorld",
    dimension: Dimension,
    structure: "Structure",
    location: BlockCoordinates,
    scale: FloatTriplet,
    rotation: FloatTriplet,
    copy_air=True,
    copy_water=True,
    copy_lava=True,
):
    for _ in paste_iter(
        world,
        dimension,
        structure,
        location,
        scale,
        rotation,
        copy_air,
        copy_water,
        copy_lava,
    ):
        pass


def paste_iter(
    world: "ChunkWorld",
    dimension: Dimension,
    structure: "Structure",
    location: BlockCoordinates,
    scale: FloatTriplet,
    rotation: FloatTriplet,
    copy_air=True,
    copy_water=True,
    copy_lava=True,
):
    yield from world.paste(
        structure,
        "main",
        structure.selection_bounds,
        dimension,
        location,
        scale,
        rotation,
        True,
        True,
        (Block("universal_minecraft", "air"),) * bool(not copy_air)
        + (Block("universal_minecraft", "water"),) * bool(not copy_water)
        + (Block("universal_minecraft", "lava"),) * bool(not copy_lava),
        True,
    )
