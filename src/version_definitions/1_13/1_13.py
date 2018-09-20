from os.path import exists, join

from nbt import nbt

from api.world import World

from formats.format_loader import loader

FORMAT = "anvil2"


def identify(directory: str) -> bool:
    if not (exists(join(directory, "region")) or exists(join(directory, "playerdata"))):
        return False

    if not (exists(join(directory, "data")) or exists(join(directory, "level.dat"))):
        return False

    fp = open(join(directory, "level.dat"), "rb")
    root_tag = nbt.NBTFile(fileobj=fp)
    fp.close()

    if "FML" in root_tag:
        return False

    if (
        root_tag.get("Data", nbt.TAG_Compound()).get("Version", nbt.TAG_Compound()).get(
            "Id", nbt.TAG_Int(-1)
        ).value
        < 1451
    ):
        return False

    return True


def load(directory: str) -> World:
    return loader["anvil2"].LEVEL_CLASS.load(directory, "1_13")
