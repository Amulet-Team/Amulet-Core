from __future__ import annotations

from amulet_nbt import TAG_Compound

from .anvil_world import AnvilFormat
from amulet.utils.format_utils import check_all_exist, load_leveldat


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
            level_dat_root = load_leveldat(path)
            assert isinstance(level_dat_root.value, TAG_Compound)
        except:
            return False

        if "Data" not in level_dat_root:
            return False

        if "FML" in level_dat_root:
            return True

        return False

    @property
    def game_version_string(self) -> str:
        try:
            return f'Java Forge {self.root_tag["Data"]["Version"]["Name"].value}'
        except Exception:
            return f"Java Forge Unknown Version"


export = AnvilForgeFormat
