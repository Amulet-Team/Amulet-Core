from api import WorldFormat
from nbt import nbt
from os import path


class AnvilWorld(WorldFormat):
    pass


def identify(directory: str) -> bool:
    if not (
        path.exists(path.join(directory, "region"))
        or path.exists(path.join(directory, "level.dat"))
    ):
        return False

    if (
        not path.exists(path.join(directory, "players"))
        and not path.exists(path.join(directory, "playerdata"))
    ):
        return False

    fp = open(path.join(directory, "level.dat"), "rb")
    root_tag = nbt.NBTFile(fileobj=fp)
    fp.close()
    if (
        root_tag.get("Data", nbt.TAG_Compound()).get("Version", nbt.TAG_Compound()).get(
            "Id", nbt.TAG_Int(-1)
        ).value
        > 1451
    ):
        return False

    return True
