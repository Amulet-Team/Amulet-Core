from __future__ import annotations

import shutil
from typing import Optional, Callable
from threading import Lock
import os
from weakref import ref

from leveldb import LevelDB
from amulet.api.cache import TempDir


class DiskCache:
    """
    A key, value database with a fast access RAM component and a longer term storage disk component.
    Keys and values are both bytes.
    The disk component is a leveldb database.
    """

    def __init__(self, path: str, max_size: int):
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

    def __del__(self):
        self._disk.close()
        shutil.rmtree(self._path, ignore_errors=True)

    @property
    def max_size(self) -> int:
        return self._max_size

    @max_size.setter
    def max_size(self, max_size: int):
        if not isinstance(max_size, int):
            raise TypeError
        with self._lock:
            self._max_size = max_size
            self._free()

    def __setitem__(self, key: bytes, value: bytes):
        with self._lock:
            self._remove(key)
            self._ram[key] = (value, True)
            self._size += len(value)
            self._free()

    def _remove(self, key: bytes):
        if key in self._ram:
            data = self._ram.pop(key)[0]
            self._size -= len(data)

    def __delitem__(self, key: bytes):
        with self._lock:
            self._remove(key)
            if key in self._disk:
                del self._disk[key]

    def _free(self):
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
            else:
                raise KeyError


class GlobalDiskCache(DiskCache):
    _instance_ref: Callable[[], Optional[GlobalDiskCache]] = lambda: None
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
    def cache_size(cls):
        instance: Optional[GlobalDiskCache] = cls._instance_ref()
        if instance is None:
            return cls._cache_size
        else:
            return instance.max_size

    @classmethod
    def set_cache_size(cls, size: int):
        instance: Optional[GlobalDiskCache] = cls._instance_ref()
        cls._cache_size = size
        if instance is not None:
            instance.max_size = size

    def __init__(self):
        self._temp_dir = TempDir()
        super().__init__(os.path.join(self._temp_dir, "history_db"), 100_000_000)
