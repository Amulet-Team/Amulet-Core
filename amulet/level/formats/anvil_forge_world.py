from __future__ import annotations
import glob
import os

from amulet_nbt import load as load_nbt

from .anvil_world import AnvilFormat
from amulet.utils.format_utils import check_all_exist


class AnvilForgeFormat(AnvilFormat):
    """
    This FormatWrapper class is a modification on the :class:`AnvilFormat` class that separates Forge worlds from vanilla worlds.

    Currently there is no extra logic here but this should extend the :class:`AnvilFormat` class to support Forge worlds.
    """

    def __init__(self, path: str):
        super().__init__(path)
        self._register_modded_dimensions()

    @staticmethod
    def is_valid(path: str) -> bool:
        if not check_all_exist(path, "level.dat"):
            return False

        try:
            level_dat_root = load_nbt(os.path.join(path, "level.dat")).compound
        except:
            return False

        return "Data" in level_dat_root and (
            "FML" in level_dat_root or "fml" in level_dat_root
        )

    @property
    def game_version_string(self) -> str:
        try:
            return f'Java Forge {self.root_tag.compound.get_compound("Data").get_compound("Version").get_string("Name").py_str}'
        except Exception:
            return f"Java Forge Unknown Version"

    def _register_modded_dimensions(self):
        for region_path in glob.glob(
            os.path.join(glob.escape(self.path), "dimensions", "*", "**", "region"),
            recursive=True,
        ):
            if not os.path.isdir(region_path):
                continue
            dim_path = os.path.dirname(region_path)
            rel_dim_path = os.path.relpath(dim_path, self.path)
            _, dimension, *base_name = rel_dim_path.split(os.sep)

            dimension_name = f"{dimension}:{'/'.join(base_name)}"
            self._register_dimension(os.path.dirname(rel_dim_path), dimension_name)


export = AnvilForgeFormat
