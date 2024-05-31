from __future__ import annotations

from .base_level import BaseLevel
from amulet.api import wrapper as api_wrapper


class Structure(BaseLevel):
    """
    Class that handles editing of any structure format via an separate and flexible data format
    """

    def __init__(
        self,
        directory: str,
        structure_wrapper: api_wrapper.StructureFormatWrapper,
    ):
        super().__init__(directory, structure_wrapper)

    @property
    def level_wrapper(self) -> api_wrapper.StructureFormatWrapper:
        """A class to access data directly from the level."""
        return self._level_wrapper
