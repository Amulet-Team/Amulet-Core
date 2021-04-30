# A cache for objects implemented using leveldb for speed.
import os
import shutil
import atexit
import time

from amulet.libs.leveldb import LevelDB
from amulet.api.paths import get_cache_dir
from amulet import log

_path = os.path.join(get_cache_dir(), "world_temp", str(int(time.time())), "db")


_cache_db = None


def _clear_db():
    if _cache_db is not None:
        log.info("Removing cache.")
        _cache_db.close(compact=False)
        shutil.rmtree(os.path.dirname(_path))


def get_cache_db() -> LevelDB:
    global _cache_db
    if _cache_db is None:
        _cache_db = LevelDB(_path, True)
        atexit.register(_clear_db)
    return _cache_db
