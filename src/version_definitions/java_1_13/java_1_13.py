from __future__ import annotations

from api.world import World
from api.blocks import Block

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


_WATER_CONSTANT = Block(blockstate="minecraft:water")


def parse_blockstate(blockstate: str) -> Block:
    namespace, base_name, properties = Block.parse_blockstate_string(blockstate)

    if properties.pop("waterlogged", "false").lower() == "true":
        block = Block(
            namespace=namespace,
            base_name=base_name,
            properties=properties,
            extra_blocks=(_WATER_CONSTANT,),
        )
    else:
        block = Block(namespace=namespace, base_name=base_name, properties=properties)

    return block


def load(directory: str) -> World:
    return loader["anvil2"].LEVEL_CLASS.load(
        directory, "java_1_13", get_blockstate_adapter=parse_blockstate
    )
