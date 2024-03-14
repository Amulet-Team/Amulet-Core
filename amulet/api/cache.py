# A cache for objects implemented using leveldb for speed.
from __future__ import annotations

from typing import IO
import os
import shutil
import time
import logging
import glob
import re
import tempfile
from weakref import finalize

import portalocker
from amulet.utils.weakref import CallableWeakMethod

log = logging.getLogger(__name__)


def _get_cache_dir() -> str:
    return os.path.join(os.environ.get("CACHE_DIR"), "level_data")


TempPattern = re.compile(r"amulettmp.*?-(?P<time>\d+)")


def _clear_temp_dirs():
    """
    Try and delete historic temporary directories.
    If things went very wrong in past sessions temporary directories may still exist.
    """
    temp_dir = tempfile.gettempdir()
    for path in glob.glob(os.path.join(glob.escape(temp_dir), "amulettmp*")):
        name = os.path.relpath(path, temp_dir)
        match = TempPattern.fullmatch(name)
        if match and int(match.group("time")) < (time.time() - 7 * 24 * 3600):
            lock_path = os.path.join(path, "lock")
            if os.path.exists(lock_path):
                with open(lock_path) as lock:
                    # make sure it is not locked by another process
                    try:
                        portalocker.lock(lock, portalocker.LockFlags.EXCLUSIVE)
                    except:
                        continue
                    else:
                        portalocker.unlock(lock)
            shutil.rmtree(path, ignore_errors=True)


_clear_temp_dirs()


class TempDir(str):
    """
    A temporary directory to do with as you wish.

    >>> t = TempDir()
    >>> path = os.path.join(t, "your_file.txt")  # TempDir is a subclass of str
    >>> # make sure all files in the temporary directory are closed before releasing or closing this object.
    >>> # The temporary directory will be deleted when the last reference to `t` is lost or when `t.close()` is called
    """

    __lock: IO | None
    __finalise: finalize

    def __new__(cls) -> TempDir:
        cache_dir = _get_cache_dir()
        os.makedirs(cache_dir, exist_ok=True)
        return super().__new__(
            cls,
            tempfile.mkdtemp(
                prefix="amulettmp",
                suffix=f"-{time.time():.0f}",
                dir=cache_dir,
            ),
        )

    def __init__(self):
        self.__lock = open(os.path.join(self, "lock"), "w")
        portalocker.lock(self.__lock, portalocker.LockFlags.EXCLUSIVE)
        self.__finalise = finalize(self, CallableWeakMethod(self.close))

    def close(self):
        """Close the lock and delete the directory."""
        if self.__lock is not None:
            portalocker.unlock(self.__lock)
            self.__lock.close()
            self.__lock = None
            shutil.rmtree(self)

    def __del__(self) -> None:
        self.__finalise()
