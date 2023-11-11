from _typeshed import Incomplete
from amulet.api.cache import TempDir as TempDir
from typing import Callable, Optional

class DiskCache:
    """
    A key, value database with a fast access RAM component and a longer term storage disk component.
    Keys and values are both bytes.
    The disk component is a leveldb database.
    """
    _lock: Incomplete
    _ram: Incomplete
    _path: Incomplete
    _disk: Incomplete
    _max_size: Incomplete
    _size: int
    def __init__(self, path: str, max_size: int) -> None:
        """
        Create a new DiskCache
        :param path: The path to save the disk component to.
        :param max_size: The maximum amount of RAM that values can occupy. Key size is assumed negligible.
            When this is overflowed, the least recently used entries are unloaded to the disk storage.
        """
    def __del__(self) -> None: ...
    @property
    def max_size(self) -> int: ...
    @max_size.setter
    def max_size(self, max_size: int) -> None: ...
    def __setitem__(self, key: bytes, value: bytes) -> None: ...
    def _remove(self, key: bytes) -> None: ...
    def __delitem__(self, key: bytes) -> None: ...
    def _free(self) -> None:
        """Push some values to disk"""
    def __getitem__(self, key: bytes) -> bytes: ...

class GlobalDiskCache(DiskCache):
    _instance_ref: Callable[[], Optional[GlobalDiskCache]]
    _cache_size: int
    @classmethod
    def instance(cls) -> GlobalDiskCache:
        """
        Get the global disk cache instance.
        The caller must store a strong reference to the returned value otherwise it will be destroyed.
        """
    @classmethod
    def cache_size(cls) -> int: ...
    @classmethod
    def set_cache_size(cls, size: int) -> None: ...
    _temp_dir: Incomplete
    def __init__(self) -> None: ...
