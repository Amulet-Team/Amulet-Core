from __future__ import annotations

import shutil
from typing import Optional, Callable, cast, IO, Self
from threading import Lock
import os
from weakref import ref, finalize
import time
import glob
import re
import tempfile

import portalocker
from leveldb import LevelDB
from amulet.utils.weakref import CallableWeakMethod


TempPattern = re.compile(r"amulettmp.*?-(?P<time>\d+)")


def _temp_dir() -> str:
    temp_dir = os.environ.get("CACHE_DIR")
    if temp_dir is None:
        raise RuntimeError
    return temp_dir


def _clear_temp_dirs() -> None:
    """
    Try and delete historic temporary directories.
    If things went very wrong in past sessions temporary directories may still exist.
    """
    for path in glob.glob(
        os.path.join(glob.escape(tempfile.gettempdir()), "amulettmp*")
    ) + glob.glob(
        os.path.join(glob.escape(_temp_dir()), "**", "amulettmp*"), recursive=True
    ):
        name = os.path.basename(path)
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

    def __new__(cls, group: str) -> Self:
        cache_dir = os.path.join(_temp_dir(), group)
        os.makedirs(cache_dir, exist_ok=True)
        return super().__new__(
            cls,
            tempfile.mkdtemp(
                prefix="amulettmp",
                suffix=f"-{time.time():.0f}",
                dir=cache_dir,
            ),
        )

    def __init__(self, group: str) -> None:
        self.__lock = open(os.path.join(self, "lock"), "w")
        portalocker.lock(self.__lock, portalocker.LockFlags.EXCLUSIVE)
        self.__finalise = finalize(self, CallableWeakMethod(self._close))

    def _close(self) -> None:
        if self.__lock is not None:
            portalocker.unlock(self.__lock)
            self.__lock.close()
            self.__lock = None
            shutil.rmtree(self)

    def close(self) -> None:
        """Close the lock and delete the directory."""
        self.__finalise()

    def __del__(self) -> None:
        self.__finalise()
