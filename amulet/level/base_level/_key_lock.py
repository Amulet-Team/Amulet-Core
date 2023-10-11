from threading import Lock, RLock
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
        self._locks: WeakKeyDictionary[T, RLock] = WeakKeyDictionary()

    def get(self, key: T) -> RLock:
        with self._lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = self._locks[key] = RLock()
            return lock
