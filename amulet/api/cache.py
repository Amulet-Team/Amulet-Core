# A cache for objects implemented using leveldb for speed.
import os
import shutil
import atexit

from amulet.libs.leveldb import LevelDB
from amulet.api.paths import get_temp_dir
from amulet import log

_path = os.path.join(get_temp_dir("cache"), "db")

CacheDB = LevelDB(_path, True)


def clear_db():
    log.info("Removing cache.")
    CacheDB.close(compact=False)
    shutil.rmtree(_path)


atexit.register(clear_db)
