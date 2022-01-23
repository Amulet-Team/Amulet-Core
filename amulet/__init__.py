import os
import argparse

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


entity_support = False
experimental_entity_support = False


def _parse_args():
    global experimental_entity_support
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experimental-entity-support",
        dest="experimental_entity_support",
        action="store_true",
    )
    args = parser.parse_known_args()[0]
    experimental_entity_support = args.experimental_entity_support


_parse_args()


IMG_DIRECTORY = os.path.join(os.path.dirname(__file__), "img")

from .api import *
from .utils.log import log
from amulet.level.load import load_level, load_format
