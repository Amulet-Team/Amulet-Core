from __future__ import annotations
import os

from amulet_nbt import load as load_nbt

from .anvil_world import AnvilFormat
from amulet.utils.format_utils import check_all_exist


class AnvilForgeFormat(AnvilFormat):
    """
    This FormatWrapper class is a modification on the :class:`AnvilFormat` class that separates Forge worlds from vanilla worlds.

    Currently there is no extra logic here but this should extend the :class:`AnvilFormat` class to support Forge worlds.
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        if not check_all_exist(path, "level.dat"):
            return False

        try:
            level_dat_root = load_nbt(os.path.join(path, "level.dat")).compound
        except:
            return False

        return "Data" in level_dat_root and "FML" in level_dat_root

    @property
    def game_version_string(self) -> str:
        try:
            return f'Java Forge {self.root_tag.compound.get_compound("Data").get_compound("Version").get_string("Name").py_str}'
        except Exception:
            return f"Java Forge Unknown Version"


export = AnvilForgeFormat
