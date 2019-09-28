from __future__ import annotations

from os.path import exists, join

from nbt import nbt


def check_all_exist(in_dir: str, *args: str) -> bool:
    """
    Check that all files exist in a parent directory

    :param in_dir: The parent directory
    :param *args: file or folder names to look for
    :return: Boolean value indicating whether all were found
    """

    for child in args:
        if not exists(join(in_dir, child)):
            print(f"Didn't find {child}")
            return False
        else:
            print(f"Found {child}")

    return True


def check_one_exists(in_dir: str, *args: str) -> bool:
    """
    Check that at least one file exists in a parent directory

    :param in_dir: The parent directory
    :param *args: file or folder names to look for
    :return: Boolean value indicating whether at least one was found
    """

    for child in args:
        if exists(join(in_dir, child)):
            print(f"Found {child}")
            return True

    return False


def load_leveldat(in_dir: str) -> nbt.TAG_Compound:
    """
    Load the root tag of the level.dat file in the directory

    :param in_dir: The world directory containing the level.dat file
    :return: The NBT root tag
    """

    fp = open(join(in_dir, "level.dat"), "rb")
    root_tag = nbt.NBTFile(fileobj=fp)
    fp.close()

    return root_tag


def check_version_leveldat(
    root_tag: nbt.TAG_Compound, _min: int = None, _max: int = None
) -> bool:
    """
    Check the Version tag from the provided level.dat NBT structure

    :param root_tag: the root level.dat tag
    :param _min: The lowest acceptable value (optional)
    :param _max: The highest acceptable value (optional)
    :return: Whether the version tag falls in the correct range
    """

    version_found: int = root_tag.get("Data", nbt.TAG_Compound()).get(
        "Version", nbt.TAG_Compound()
    ).get("Id", nbt.TAG_Int(-1)).value

    min_qualifies: bool = True
    if _min is not None:
        min_qualifies = version_found >= _min

    max_qualifies: bool = True
    if _max is not None:
        max_qualifies = version_found <= _max

    if __debug__:
        min_text: str = f"{min} <= " if _min is not None else ""
        max_text: str = f" <= {max}" if _max is not None else ""
        print(f"Checking {min_text}{version_found}{max_text}")

    return min_qualifies and max_qualifies
