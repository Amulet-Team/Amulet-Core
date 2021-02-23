# A cache for objects implemented using leveldb for speed.
import os
import shutil
import atexit

from amulet.libs.leveldb import LevelDB
from amulet.api.paths import get_temp_dir
from amulet import log

_path = os.path.join(get_temp_dir("cache"), "db")


_cache_db = None


def _clear_db():
    if _cache_db is not None:
        log.info("Removing cache.")
        _cache_db.close(compact=False)
        shutil.rmtree(_path)


def get_cache_db() -> LevelDB:
    global _cache_db
    if _cache_db is None:
        _cache_db = LevelDB(_path, True)
        atexit.register(_clear_db)
    return _cache_db
