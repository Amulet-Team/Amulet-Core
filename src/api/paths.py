import sys
import os

from typing import Sequence, Union

_executable_dir = os.path.dirname(sys.executable)
_script_base = os.path.dirname(sys.argv[0])
_package_base = os.path.dirname(os.path.dirname(__file__))


def _application_directory(
    directory: Union[str, Sequence[str]], src_path: Union[str, Sequence[str]] = None
) -> str:
    """
    Returns a path to a directory that is adjusted depending on whether the program is running in a compiled or as source.
    The necessary directories will be created if they aren't already present.

    If the ```sys``` module has a "testing" attribute and it's True, then the path won't be created.

    :param directory: The directory or directories to get the full path of and/or create
    :param src_path: Fallback option if the directory location of a compiled build vs. running from source differ
    :return: The full path to the resulting directory
    """
    if isinstance(directory, str):
        directory = (directory,)

    if getattr(sys, "frozen", False):
        path = os.path.join(_executable_dir, *directory)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    if src_path:
        if isinstance(src_path, str):
            directory = (src_path,)
        else:
            directory = src_path

    if getattr(sys, "testing", False):
        return os.path.join(_package_base, *directory)

    else:
        path = os.path.join(_script_base, *directory)
        if not os.path.exists(path):
            os.makedirs(path)
        return path


FORMATS_DIR = _application_directory("formats")
COMMANDS_DIR = _application_directory("commands", ("command_line", "commands"))
DEFINITIONS_DIR = _application_directory("definitions", "version_definitions")

# WORK_DIR = _application_directory("work")
