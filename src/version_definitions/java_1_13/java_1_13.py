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

    # 1444 is the version for 17w43a snapshot (first 1.13 snapshot)
    # 1519 is the version for the 1.13 release version
    # 1628 is the version for the 1.13.1 release version
    if not check_version_leveldat(leveldat_root, _min=1444, _max=1628):
        return False

    return True


def load(directory: str) -> World:
    return loader["anvil2"].LEVEL_CLASS.load(directory, "java_1_13")
