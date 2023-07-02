import os
import logging
import platformdirs

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


entity_support = False

IMG_DIRECTORY = os.path.join(os.path.dirname(__file__), "img")

# Initialise default paths. Applications should override these environment variables.
# os.environ.setdefault("DATA_DIR", platformdirs.user_data_dir("AmuletTeam", "AmuletTeam"))
# os.environ.setdefault("CONFIG_DIR", platformdirs.user_config_dir("AmuletTeam", "AmuletTeam"))
os.environ.setdefault(
    "CACHE_DIR", platformdirs.user_cache_dir("AmuletTeam", "AmuletTeam")
)
os.environ.setdefault("LOG_DIR", platformdirs.user_log_dir("AmuletTeam", "AmuletTeam"))

from .api import *
from amulet.level.load import load_level, load_format

# init a default logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
