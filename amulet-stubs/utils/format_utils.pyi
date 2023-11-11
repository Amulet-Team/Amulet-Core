from amulet_nbt import NamedTag as NamedTag

def check_all_exist(in_dir: str, *args: str) -> bool:
    """
    Check that all files exist in a parent directory

    :param in_dir: The parent directory
    :param args: file or folder names to look for
    :return: Boolean value indicating whether all were found
    """
def check_one_exists(in_dir: str, *args: str) -> bool:
    """
    Check that at least one file exists in a parent directory

    :param in_dir: The parent directory
    :param args: file or folder names to look for
    :return: Boolean value indicating whether at least one was found
    """
def load_leveldat(in_dir: str) -> NamedTag:
    """
    Load the root tag of the level.dat file in the directory

    :param in_dir: The world directory containing the level.dat file
    :return: The NBT root tag
    """
