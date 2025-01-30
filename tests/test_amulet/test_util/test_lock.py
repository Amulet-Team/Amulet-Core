from unittest import TestCase
import weakref
import time
from threading import Thread, Condition

from amulet.utils.task_manager import AbstractCancelManager, CancelManager
from amulet.utils.mutex import OrderedSharedTimedMutex, Deadlock
from amulet.utils.lock import OrderedSharedLock, LockNotAcquired, Lock, RLock

class LockTestCase(TestCase):
    def test_lock(self) -> None:
        lock = Lock()
        with lock:
            self.assertTrue(True)

    def test_parallel_context_manager(self) -> None:
        condition = Condition()
        lock = Lock()

        exec_order: list[int] = []
        end_times: list[float] = []
        thread_count = 0

        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        def f1():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 2)
            with lock:
                increment_thread_count()
                exec_order.append(1)
                time.sleep(1)
                exec_order.append(2)
            end_times.append(time.time())

        def f2():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 3)
            with lock:
                increment_thread_count()
                exec_order.append(3)
                time.sleep(1)
                exec_order.append(4)
            end_times.append(time.time())

        thread_1 = Thread(target=f1)
        thread_2 = Thread(target=f2)

        thread_1.start()
        thread_2.start()

        with condition:
            condition.wait_for(lambda: thread_count == 2)
        t = time.time()

        thread_1.join()
        thread_2.join()

        self.assertEqual([1, 2, 3, 4], exec_order)

        dt = max(end_times) - t
        self.assertTrue(
            1.99 <= dt <= 2.5,
            f"Expected 0.5s. Got {dt}s",
        )

    def test_parallel_methods(self) -> None:
        condition = Condition()
        lock = Lock()

        exec_order: list[int] = []
        end_times: list[float] = []
        thread_count = 0

        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        def f1():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 2)
            lock.acquire()
            increment_thread_count()
            exec_order.append(1)
            time.sleep(1)
            exec_order.append(2)
            lock.release()
            end_times.append(time.time())

        def f2():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 3)
            lock.acquire()
            increment_thread_count()
            exec_order.append(3)
            time.sleep(1)
            exec_order.append(4)
            lock.release()
            end_times.append(time.time())

        thread_1 = Thread(target=f1)
        thread_2 = Thread(target=f2)

        thread_1.start()
        thread_2.start()

        with condition:
            condition.wait_for(lambda: thread_count == 2)
        t = time.time()

        thread_1.join()
        thread_2.join()

        self.assertEqual([1, 2, 3, 4], exec_order)

        dt = max(end_times) - t
        self.assertTrue(
            1.99 <= dt <= 2.5,
            f"Expected 0.5s. Got {dt}s",
        )

class RLockTestCase(TestCase):
    def test_rlock(self) -> None:
        lock = RLock()
        with lock:
            with lock:
                self.assertTrue(True)

    def test_parallel_context_manager(self) -> None:
        condition = Condition()
        lock = RLock()

        exec_order: list[int] = []
        end_times: list[float] = []
        thread_count = 0

        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        def f1():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 2)
            with lock:
                increment_thread_count()
                exec_order.append(1)
                time.sleep(1)
                exec_order.append(2)
            end_times.append(time.time())

        def f2():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 3)
            with lock:
                increment_thread_count()
                exec_order.append(3)
                time.sleep(1)
                exec_order.append(4)
            end_times.append(time.time())

        thread_1 = Thread(target=f1)
        thread_2 = Thread(target=f2)

        thread_1.start()
        thread_2.start()

        with condition:
            condition.wait_for(lambda: thread_count == 2)
        t = time.time()

        thread_1.join()
        thread_2.join()

        self.assertEqual([1, 2, 3, 4], exec_order)

        dt = max(end_times) - t
        self.assertTrue(
            1.99 <= dt <= 2.5,
            f"Expected 0.5s. Got {dt}s",
        )

    def test_parallel_methods(self) -> None:
        condition = Condition()
        lock = RLock()

        exec_order: list[int] = []
        end_times: list[float] = []
        thread_count = 0

        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        def f1():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 2)
            lock.acquire()
            increment_thread_count()
            exec_order.append(1)
            time.sleep(1)
            exec_order.append(2)
            lock.release()
            end_times.append(time.time())

        def f2():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 3)
            lock.acquire()
            increment_thread_count()
            exec_order.append(3)
            time.sleep(1)
            exec_order.append(4)
            lock.release()
            end_times.append(time.time())

        thread_1 = Thread(target=f1)
        thread_2 = Thread(target=f2)

        thread_1.start()
        thread_2.start()

        with condition:
            condition.wait_for(lambda: thread_count == 2)
        t = time.time()

        thread_1.join()
        thread_2.join()

        self.assertEqual([1, 2, 3, 4], exec_order)

        dt = max(end_times) - t
        self.assertTrue(
            1.99 <= dt <= 2.5,
            f"Expected 0.5s. Got {dt}s",
        )

class OrderedLockTestCase(TestCase):
    def test_lock_not_acquired(self) -> None:
        self.assertTrue(issubclass(LockNotAcquired, RuntimeError))
        with self.assertRaises(RuntimeError):
            raise LockNotAcquired
        with self.assertRaises(LockNotAcquired):
            raise LockNotAcquired

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

    def test_parallel(self) -> None:
        lock = OrderedSharedLock()
        condition = Condition()

        exec_order: list[str] = []
        end_times: list[float] = []
        thread_count = 0

        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        sleep_time = 1

        def parallel_func_1():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 5)
            with lock.shared(timeout=5):
                increment_thread_count()
                exec_order.append("shared")
                time.sleep(sleep_time)
                exec_order.append("shared")
            end_times.append(time.time())

        def serial_func():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 7)
            with lock.unique(timeout=5):
                increment_thread_count()
                exec_order.append("unique")
                time.sleep(sleep_time)
                exec_order.append("unique")
            end_times.append(time.time())

        def parallel_func_2():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            with lock.shared(timeout=5):
                increment_thread_count()
                exec_order.append("shared")
                time.sleep(sleep_time)
                exec_order.append("shared")
            end_times.append(time.time())

        thread_1 = Thread(target=parallel_func_1)
        thread_2 = Thread(target=parallel_func_1)
        thread_3 = Thread(target=serial_func)
        thread_4 = Thread(target=parallel_func_2)
        thread_5 = Thread(target=parallel_func_2)

        # Start threads
        thread_1.start()
        thread_2.start()
        thread_3.start()
        thread_4.start()
        thread_5.start()

        # Wait for all threads to start
        with condition:
            condition.wait_for(lambda: thread_count >= 5)
        # Get start time
        t = time.time()

        # Wait for threads to finish
        thread_1.join()
        thread_2.join()
        thread_3.join()
        thread_4.join()
        thread_5.join()

        dt = max(end_times) - t

        # validate order
        self.assertEqual(
            [
                "shared",
                "shared",
                "shared",
                "shared",
                "unique",
                "unique",
                "shared",
                "shared",
                "shared",
                "shared",
            ],
            exec_order,
        )

        expected_time = sleep_time * 3
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.5,
            f"Expected {expected_time}s. Got {dt}s",
        )

    def test_timeout(self) -> None:
        result_1 = False
        result_2 = False

        lock = OrderedSharedLock()
        condition = Condition()

        end_times: list[float] = []
        thread_count = 0

        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        def func_1():
            nonlocal result_1
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 2)
            try:
                with lock.unique(blocking=False):
                    increment_thread_count()
                    time.sleep(1)
            except LockNotAcquired:
                result_1 = False
            else:
                result_1 = True
            end_times.append(time.time())

        def func_2():
            nonlocal result_2
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 3)
            try:
                with lock.unique(timeout=0.1):
                    time.sleep(1)
            except LockNotAcquired:
                result_2 = True
            else:
                result_2 = False
            end_times.append(time.time())

        thread_1 = Thread(target=func_1)
        thread_2 = Thread(target=func_2)

        # Start threads
        thread_1.start()
        thread_2.start()

        # Wait for all threads to start
        with condition:
            condition.wait_for(lambda: thread_count >= 2)
        # Get start time
        t = time.time()

        # Wait for threads to finish
        thread_1.join()
        thread_2.join()

        dt = max(end_times) - t

        self.assertTrue(
            0.99 <= dt <= 1.5,
            f"Expected 1s. Got {dt}s",
        )

        self.assertTrue(result_1)
        self.assertTrue(result_2)

    def test_cancel(self) -> None:
        for timeout in [-1, 10]:
            with self.subTest(timeout=timeout):
                result_1 = False
                result_2 = False

                lock_1 = OrderedSharedLock()
                lock_2 = OrderedSharedLock()

                condition = Condition()
                end_times: list[float] = []
                thread_count = 0

                def increment_thread_count():
                    nonlocal thread_count
                    thread_count += 1
                    with condition:
                        condition.notify_all()

                def func_1(cancel_manager: AbstractCancelManager):
                    nonlocal result_1
                    increment_thread_count()
                    with condition:
                        condition.wait_for(lambda: thread_count >= 3)
                    with lock_1.unique(blocking=False):
                        increment_thread_count()
                        with condition:
                            condition.wait_for(lambda: thread_count >= 5)
                        with lock_2.unique(
                            cancel_manager=cancel_manager, timeout=timeout
                        ):
                            result_1 = True
                    end_times.append(time.time())

                def func_2(cancel_manager: AbstractCancelManager):
                    nonlocal result_2
                    increment_thread_count()
                    with condition:
                        condition.wait_for(lambda: thread_count >= 3)
                    with lock_2.unique(blocking=False):
                        increment_thread_count()
                        with condition:
                            condition.wait_for(lambda: thread_count >= 5)
                        time.sleep(1)
                        try:
                            with lock_1.unique(
                                cancel_manager=cancel_manager, timeout=timeout
                            ):
                                pass
                        except LockNotAcquired:
                            result_2 = True
                    end_times.append(time.time())

                cancel_manager_1 = CancelManager()
                cancel_manager_2 = CancelManager()

                thread_1 = Thread(target=func_1, args=(cancel_manager_1,))
                thread_2 = Thread(target=func_2, args=(cancel_manager_2,))

                # Start threads
                thread_1.start()
                thread_2.start()

                # Wait for all threads to start
                with condition:
                    condition.wait_for(lambda: thread_count >= 2)
                # Get start time
                t = time.time()
                increment_thread_count()

                time.sleep(2)

                cancel_manager_2.cancel()

                # Wait for threads to finish
                thread_1.join()
                thread_2.join()

                dt = max(end_times) - t

                self.assertTrue(result_1)
                self.assertTrue(result_2)

                self.assertTrue(
                    1.99 <= dt <= 2.5,
                    f"Expected 0.5s. Got {dt}s",
                )
