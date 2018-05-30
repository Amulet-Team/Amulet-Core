from api import WorldFormat
from nbt import nbt
from os import path


class Anvil2World(WorldFormat):

    @classmethod
    def load(cls, directory: str) -> object:
        pass

    @classmethod
    def fromUnifiedFormat(cls, unified: object) -> object:
        pass

    def toUnifiedFormat(self) -> object:
        pass

    def save(self) -> None:
        pass


def identify(directory: str) -> bool:
    if not (
        path.exists(path.join(directory, "region"))
        or path.exists(path.join(directory, "playerdata"))
    ):
        return False

    if not (
        path.exists(path.join(directory, "DIM1"))
        or path.exists(path.join(directory, "DIM-1"))
    ):
        return False

    if not (
        path.exists(path.join(directory, "data"))
        or path.exists(path.join(directory, "level.dat"))
    ):
        return False

    fp = open(path.join(directory, "level.dat"), "rb")
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
