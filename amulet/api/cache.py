# A cache for objects implemented using leveldb for speed.
import os
import shutil
import atexit
import time
import logging

from amulet.libs.leveldb import LevelDB
from amulet.api.paths import get_cache_dir

log = logging.getLogger(__name__)

_temp_path = os.path.join(get_cache_dir(), "world_temp")
_path = os.path.join(_temp_path, str(int(time.time())), "db")


_cache_db = None


def _clear_db():
    if _cache_db is not None:
        log.info("Removing cache.")
        _cache_db.close(compact=False)
        shutil.rmtree(os.path.dirname(_path))

    # remove all cache directories that were created before a week ago
    # Sometimes if the program is stopped or it crashes the cleanup won't happen
    for t in os.listdir(_temp_path):
        if t.isnumeric() and int(t) < (time.time() - 7 * 24 * 3600):
            try:
                shutil.rmtree(os.path.join(_temp_path, t))
            except:
                pass


def get_cache_db() -> LevelDB:
    global _cache_db
    if _cache_db is None:
        _cache_db = LevelDB(_path, True)
        atexit.register(_clear_db)
    return _cache_db
