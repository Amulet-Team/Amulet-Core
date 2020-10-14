from __future__ import annotations

from typing import TYPE_CHECKING

from .chunk_world import ChunkWorld

if TYPE_CHECKING:
    from amulet.api.wrapper import StructureFormatWrapper


class Structure(ChunkWorld):
    """
    Class that handles editing of any structure format via an separate and flexible data format
    """

    def __init__(
        self,
        directory: str,
        structure_wrapper: "StructureFormatWrapper",
        temp_dir: str = None,
    ):
        super().__init__(directory, structure_wrapper, temp_dir)
