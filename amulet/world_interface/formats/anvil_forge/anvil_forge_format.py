from __future__ import annotations

from amulet.world_interface.formats.anvil.anvil_format import AnvilFormat
from amulet.utils.format_utils import check_all_exist, load_leveldat
from amulet import log


class AnvilForgeFormat(AnvilFormat):
    @staticmethod
    def is_valid(directory) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        if not check_all_exist(directory, "level.dat"):
            return False

        try:
            level_dat_root = load_leveldat(directory)
        except:
            return False

        if "Data" not in level_dat_root:
            return False

        if "FML" in level_dat_root:
            return True

        log.info("Forge support is experimental. Use at your own risk.")
        return True

    @property
    def game_version_string(self) -> str:
        try:
            return f'Java Forge {self.root_tag["Data"]["Version"]["Name"].value}'
        except Exception:
            return f"Java Forge Unknown Version"


FORMAT_CLASS = AnvilForgeFormat
