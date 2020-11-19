# A cache for objects implemented using leveldb for speed.
import os
import shutil
import atexit

from amulet.libs.leveldb import LevelDB
from amulet.api.paths import get_temp_dir

_path = os.path.join(get_temp_dir("cache"), "db")

CacheDB = LevelDB(_path, True)


def clear_db():
    CacheDB.close()
    shutil.rmtree(_path)


atexit.register(clear_db)
