import os
import logging
import platformdirs

from . import _version

__version__ = _version.get_versions()["version"]

# Initialise default paths. Applications should override these environment variables.
# os.environ.setdefault("DATA_DIR", platformdirs.user_data_dir("AmuletTeam", "AmuletTeam"))
# os.environ.setdefault("CONFIG_DIR", platformdirs.user_config_dir("AmuletTeam", "AmuletTeam"))
os.environ.setdefault(
    "CACHE_DIR", platformdirs.user_cache_dir("AmuletTeam", "AmuletTeam")
)
os.environ.setdefault("LOG_DIR", platformdirs.user_log_dir("AmuletTeam", "AmuletTeam"))
os.makedirs(os.environ["CACHE_DIR"], exist_ok=True)
os.makedirs(os.environ["LOG_DIR"], exist_ok=True)

# init a default logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def _init() -> None:
    import os
    import sys
    import ctypes

    if sys.platform == "win32":
        lib_path = os.path.join(os.path.dirname(__file__), "amulet_core.dll")
    elif sys.platform == "darwin":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_core.dylib")
    elif sys.platform == "linux":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_core.so")
    else:
        raise RuntimeError(f"Unsupported platform {sys.platform}")

    # Import dependencies
    import amulet.nbt

    # Load the shared library
    ctypes.cdll.LoadLibrary(lib_path)

    from ._amulet import init

    init(sys.modules[__name__])


_init()
