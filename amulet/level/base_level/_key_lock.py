from threading import Lock
from weakref import WeakKeyDictionary
from typing import Generic, TypeVar


T = TypeVar("T")


class KeyLock(Generic[T]):
    """
    A map from weakly referenced keys to locks per key.
    This is useful if you want to lock access to individual resources.
    """

    def __init__(self):
        self._lock = Lock()
        self._locks: WeakKeyDictionary[T, Lock] = WeakKeyDictionary()

    def get(self, key: T) -> Lock:
        with self._lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = self._locks[key] = Lock()
            return lock
