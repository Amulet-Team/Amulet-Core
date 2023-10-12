from threading import Lock, RLock
from weakref import WeakValueDictionary
from typing import Generic, TypeVar


T = TypeVar("T")


class LockMap(Generic[T]):
    """
    A map from keys to a weakly referenced lock per key.
    This is useful if you want to lock access to individual resources.
    A strong reference to the lock must be held by the caller until it is released.
    """

    def __init__(self):
        self._lock = Lock()
        self._locks: WeakValueDictionary[T, RLock] = WeakValueDictionary()

    def get(self, key: T) -> RLock:
        with self._lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = self._locks[key] = RLock()
            return lock
