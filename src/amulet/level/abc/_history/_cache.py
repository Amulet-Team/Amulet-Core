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


class DiskCache:
    """
    A key, value database with a fast access RAM component and a longer term storage disk component.
    Keys and values are both bytes.
    The disk component is a leveldb database.
    """

    def __init__(self, path: str, max_size: int) -> None:
        """
        Create a new DiskCache
        :param path: The path to save the disk component to.
        :param max_size: The maximum amount of RAM that values can occupy. Key size is assumed negligible.
            When this is overflowed, the least recently used entries are unloaded to the disk storage.
        """
        self._lock = Lock()
        self._ram: dict[bytes, tuple[bytes, bool]] = {}
        self._path = path
        self._disk = LevelDB(path, create_if_missing=True)
        self._max_size: int = max_size
        self._size: int = 0
        self.__finalise = finalize(self, CallableWeakMethod(self._close))

    def _close(self) -> None:
        self._disk.close()
        shutil.rmtree(self._path, ignore_errors=True)

    def __del__(self) -> None:
        self.__finalise()

    @property
    def max_size(self) -> int:
        return self._max_size

    @max_size.setter
    def max_size(self, max_size: int) -> None:
        if not isinstance(max_size, int):
            raise TypeError
        with self._lock:
            self._max_size = max_size
            self._free()

    def __setitem__(self, key: bytes, value: bytes) -> None:
        with self._lock:
            self._remove(key)
            self._ram[key] = (value, True)
            self._size += len(value)
            self._free()

    def _remove(self, key: bytes) -> None:
        if key in self._ram:
            data = self._ram.pop(key)[0]
            self._size -= len(data)

    def __delitem__(self, key: bytes) -> None:
        with self._lock:
            self._remove(key)
            if key in self._disk:
                del self._disk[key]

    def _free(self) -> None:
        """Push some values to disk"""
        if self._size > self._max_size:
            keys = iter(self._ram.copy())
            while self._size > self._max_size:
                key = next(keys)
                value, changed = self._ram.pop(key)
                self._size -= len(value)
                if changed:
                    self._disk[key] = value

    def __getitem__(self, key: bytes) -> bytes:
        with self._lock:
            if key in self._ram:
                value = self._ram.pop(key)
                # Push it to the end
                self._ram[key] = value
                return value[0]
            elif key in self._disk:
                data = self._disk[key]
                self._ram[key] = (data, False)
                self._size += len(data)
                self._free()
                return data
            else:
                raise KeyError


class GlobalDiskCache(DiskCache):
    _instance_ref: Callable[[], Optional[GlobalDiskCache]] = cast(
        Callable[[], Optional["GlobalDiskCache"]], lambda: None
    )
    _cache_size = 100_000_000

    @classmethod
    def instance(cls) -> GlobalDiskCache:
        """
        Get the global disk cache instance.
        The caller must store a strong reference to the returned value otherwise it will be destroyed.
        """
        instance: Optional[GlobalDiskCache] = cls._instance_ref()
        if instance is None:
            instance = GlobalDiskCache()
            cls._instance_ref = ref(instance)
        return instance

    @classmethod
    def cache_size(cls) -> int:
        instance: Optional[GlobalDiskCache] = cls._instance_ref()
        if instance is None:
            return cls._cache_size
        else:
            return instance.max_size

    @classmethod
    def set_cache_size(cls, size: int) -> None:
        instance: Optional[GlobalDiskCache] = cls._instance_ref()
        cls._cache_size = size
        if instance is not None:
            instance.max_size = size

    def __init__(self) -> None:
        self._temp_dir = TempDir("level_data")
        super().__init__(os.path.join(self._temp_dir, "history_db"), 100_000_000)
