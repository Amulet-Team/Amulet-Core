import os
import logging

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


entity_support = False

IMG_DIRECTORY = os.path.join(os.path.dirname(__file__), "img")

from .api import *
from amulet.level.load import load_level, load_format

# init a default logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
