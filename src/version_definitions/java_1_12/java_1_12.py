from __future__ import annotations

from utils.format_utils import (
    check_all_exist,
    check_one_exists,
    load_leveldat,
    check_version_leveldat,
)

from api.world import World

from formats.format_loader import loader

FORMAT = "anvil"


def identify(directory: str) -> bool:
    if not check_all_exist(directory, "region", "level.dat"):
        return False

    if not check_one_exists(directory, "playerdata", "players"):
        return False

    leveldat_root = load_leveldat(directory)

    if "FML" in leveldat_root:
        return False

    if not check_version_leveldat(leveldat_root, _max=1343):
        return False

    return True


def load(directory: str) -> World:
    return loader["anvil"].LEVEL_CLASS.load(directory, "java_1_12")
