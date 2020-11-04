from __future__ import annotations

from typing import TYPE_CHECKING

from .base_level import BaseLevel

if TYPE_CHECKING:
    from amulet.api.wrapper import StructureFormatWrapper


class Structure(BaseLevel):
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

    @property
    def level_wrapper(self) -> "StructureFormatWrapper":
        """A class to access data directly from the level."""
        return self._level_wrapper
