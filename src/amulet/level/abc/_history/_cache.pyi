from typing import Self

from _typeshed import Incomplete
from amulet.utils.weakref import CallableWeakMethod as CallableWeakMethod

TempPattern: Incomplete

class TempDir(str):
    """
    A temporary directory to do with as you wish.

    >>> t = TempDir()
    >>> path = os.path.join(t, "your_file.txt")  # TempDir is a subclass of str
    >>> # make sure all files in the temporary directory are closed before releasing or closing this object.
    >>> # The temporary directory will be deleted when the last reference to `t` is lost or when `t.close()` is called
    """

    def __new__(cls, group: str) -> Self: ...
    def __init__(self, group: str) -> None: ...
    def close(self) -> None:
        """Close the lock and delete the directory."""

    def __del__(self) -> None: ...

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

    def __del__(self) -> None: ...
    @property
    def max_size(self) -> int: ...
    @max_size.setter
    def max_size(self, max_size: int) -> None: ...
    def __setitem__(self, key: bytes, value: bytes) -> None: ...
    def __delitem__(self, key: bytes) -> None: ...
    def __getitem__(self, key: bytes) -> bytes: ...

class GlobalDiskCache(DiskCache):
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
    def __init__(self) -> None: ...
