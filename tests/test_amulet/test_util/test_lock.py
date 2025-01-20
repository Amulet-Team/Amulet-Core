from unittest import TestCase
import weakref

from amulet.utils.mutex import OrderedSharedTimedMutex, Deadlock
from amulet.utils.lock import OrderedSharedLock, LockNotAcquired


class LockTestCase(TestCase):
    def test_lock_not_acquired(self) -> None:
        self.assertTrue(issubclass(LockNotAcquired, RuntimeError))

    def test_empty_constructor(self) -> None:
        lock = OrderedSharedLock()
        self.assertTrue(lock.acquire_unique(False))
        lock.release_unique()

    def test_mutex_constructor(self) -> None:
        mutex = OrderedSharedTimedMutex()
        lock = OrderedSharedLock(mutex)
        self.assertTrue(lock.acquire_unique(False))
        lock.release_unique()

    def test_mutex_lifespan(self) -> None:
        mutex = OrderedSharedTimedMutex()
        mutex_ref = weakref.ref(mutex)
        lock = OrderedSharedLock(mutex)
        del mutex
        self.assertIsNotNone(mutex_ref())
        del lock
        self.assertIsNone(mutex_ref())

    def test_unique_lifespan(self) -> None:
        lock = OrderedSharedLock()
        lock_ref = weakref.ref(lock)
        unique = lock.unique()
        del lock
        self.assertIsNotNone(lock_ref())
        del unique
        self.assertIsNone(lock_ref())

    def test_shared_lifespan(self) -> None:
        lock = OrderedSharedLock()
        lock_ref = weakref.ref(lock)
        shared = lock.shared()
        del lock
        self.assertIsNotNone(lock_ref())
        del shared
        self.assertIsNone(lock_ref())

    def test_exceptions(self) -> None:
        lock = OrderedSharedLock()
        with lock.unique():
            with self.assertRaises(Deadlock):
                with lock.unique():
                    pass
            with self.assertRaises(Deadlock):
                with lock.shared():
                    pass
            with self.assertRaises(Deadlock):
                lock.acquire_unique(True)
            with self.assertRaises(Deadlock):
                lock.acquire_unique(False)
            with self.assertRaises(Deadlock):
                lock.acquire_shared(True)
            with self.assertRaises(Deadlock):
                lock.acquire_shared(False)
        with lock.shared():
            with self.assertRaises(Deadlock):
                with lock.unique():
                    pass
            with self.assertRaises(Deadlock):
                with lock.shared():
                    pass
            with self.assertRaises(Deadlock):
                lock.acquire_unique(True)
            with self.assertRaises(Deadlock):
                lock.acquire_unique(False)
            with self.assertRaises(Deadlock):
                lock.acquire_shared(True)
            with self.assertRaises(Deadlock):
                lock.acquire_shared(False)
