from __future__ import annotations

from typing import TYPE_CHECKING

from .chunk_world import ChunkWorld

if TYPE_CHECKING:
    from amulet.api.wrapper import WorldFormatWrapper


class World(ChunkWorld):
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """

    def __init__(
            self, directory: str, world_wrapper: "WorldFormatWrapper", temp_dir: str = None
    ):
        super().__init__(directory, world_wrapper, temp_dir)
