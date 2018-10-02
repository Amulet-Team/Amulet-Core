from __future__ import annotations

from api.world import World

from formats.format_loader import loader

from utils.format_utils import check_all_exist, load_leveldat, check_version_leveldat

FORMAT = "anvil2"


def identify(directory: str) -> bool:
    if not check_all_exist(directory, "region", "playerdata", "data", "level.dat"):
        return False

    leveldat_root = load_leveldat(directory)

    if "FML" in leveldat_root:
        return False

    if not check_version_leveldat(leveldat_root, min=1451):
        return False

    return True


def load(directory: str) -> World:
    return loader["anvil2"].LEVEL_CLASS.load(directory, "java_1_13")
