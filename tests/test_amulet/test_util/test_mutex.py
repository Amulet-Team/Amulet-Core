import unittest
from datetime import timedelta, datetime
from threading import Thread, RLock, Condition
import time

from amulet.utils.mutex import OrderedSharedMutex, OrderedSharedTimedMutex, Deadlock
from amulet.utils.task_manager import (
    CancelManager,
    TaskCancelled,
    AbstractCancelManager,
)
from tests.test_amulet.test_util.test_mutex_ import throw_deadlock


class MutexTestCase(unittest.TestCase):
    def test_deadlock(self) -> None:
        self.assertTrue(issubclass(Deadlock, RuntimeError))

        with self.assertRaises(RuntimeError):
            raise Deadlock
        with self.assertRaises(Deadlock):
            raise Deadlock
        with self.assertRaises(RuntimeError):
            throw_deadlock()
        with self.assertRaises(Deadlock):
            throw_deadlock()

    def _test_self_deadlock(self, mutex):
        """Test that a deadlock exception is raised when locking an already locked mutex."""
        with self.assertRaises(Deadlock):
            mutex.lock()
        with self.assertRaises(Deadlock):
            mutex.try_lock()
        with self.assertRaises(Deadlock):
            mutex.lock_shared()
        with self.assertRaises(Deadlock):
            mutex.try_lock_shared()
        if isinstance(mutex, OrderedSharedTimedMutex):
            with self.assertRaises(Deadlock):
                mutex.try_lock_for(timedelta(seconds=1))
            with self.assertRaises(Deadlock):
                mutex.try_lock_until(datetime.now() + timedelta(seconds=1))
            with self.assertRaises(Deadlock):
                mutex.try_lock_for(timedelta(seconds=1))
            with self.assertRaises(Deadlock):
                mutex.try_lock_shared_until(datetime.now() + timedelta(seconds=1))

    def test_lock(self) -> None:
        mutex = OrderedSharedMutex()
        mutex.lock()
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock_shared()
        mutex.unlock()

    def test_try_lock(self) -> None:
        mutex = OrderedSharedMutex()
        mutex.try_lock()
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock_shared()
        mutex.unlock()

    def test_lock_shared(self) -> None:
        mutex = OrderedSharedMutex()
        mutex.lock_shared()
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock()
        mutex.unlock_shared()

    def test_try_lock_shared(self) -> None:
        mutex = OrderedSharedMutex()
        self.assertTrue(mutex.try_lock_shared())
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock()
        mutex.unlock_shared()

    def test_try_lock_for(self) -> None:
        mutex = OrderedSharedTimedMutex()
        self.assertTrue(mutex.try_lock_for(timedelta(seconds=1)))
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock_shared()
        mutex.unlock()

    def test_try_lock_shared_for(self) -> None:
        mutex = OrderedSharedTimedMutex()
        self.assertTrue(mutex.try_lock_shared_for(timedelta(seconds=1)))
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock()
        mutex.unlock_shared()

    def test_try_lock_until(self) -> None:
        mutex = OrderedSharedTimedMutex()
        self.assertTrue(mutex.try_lock_until(datetime.now() + timedelta(seconds=1)))
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock_shared()
        mutex.unlock()

    def test_try_lock_shared_until(self) -> None:
        mutex = OrderedSharedTimedMutex()
        self.assertTrue(
            mutex.try_lock_shared_until(datetime.now() + timedelta(seconds=1))
        )
        self._test_self_deadlock(mutex)
        with self.assertRaises(RuntimeError):
            mutex.unlock()
        mutex.unlock_shared()

    def test_threads_1(self) -> None:
        """Test 4 threads in parallel followed by 1 serial."""
        mutex = OrderedSharedMutex()
        condition = Condition()

        exec_order: list[str] = []
        end_times: list[float] = []
        thread_count = 0
        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        def thread_shared():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 5)
            mutex.lock_shared()
            increment_thread_count()
            exec_order.append("shared")
            time.sleep(1)
            exec_order.append("shared")
            mutex.unlock_shared()
            end_times.append(time.time())

        def thread_unique():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 9)
            mutex.lock()
            increment_thread_count()
            exec_order.append("unique")
            time.sleep(1)
            exec_order.append("unique")
            mutex.unlock()
            end_times.append(time.time())

        thread_1 = Thread(target=thread_shared)
        thread_2 = Thread(target=thread_shared)
        thread_3 = Thread(target=thread_shared)
        thread_4 = Thread(target=thread_shared)
        thread_5 = Thread(target=thread_unique)

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

        self.assertEqual(10, thread_count)

        dt = max(end_times) - t

        # validate order
        self.assertEqual(["shared", "shared", "shared", "shared", "shared", "shared", "shared", "shared", "unique", "unique"], exec_order)

        # Validate time
        expected_time = 2
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.5,
            f"Expected {expected_time}s. Got {dt}s",
        )

    def test_threads_2(self) -> None:
        """Test 2 threads in parallel followed by 1 serial then another 2 parallel."""
        mutex = OrderedSharedMutex()
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

        def thread_shared_1():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 5)
            mutex.lock_shared()
            increment_thread_count()
            exec_order.append("shared")
            time.sleep(sleep_time)
            exec_order.append("shared")
            mutex.unlock_shared()
            end_times.append(time.time())

        def thread_unique():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 7)
            mutex.lock()
            increment_thread_count()
            exec_order.append("unique")
            time.sleep(sleep_time)
            exec_order.append("unique")
            mutex.unlock()
            end_times.append(time.time())

        def thread_shared_2():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            mutex.lock_shared()
            increment_thread_count()
            exec_order.append("shared")
            time.sleep(sleep_time)
            exec_order.append("shared")
            mutex.unlock_shared()
            end_times.append(time.time())

        thread_1 = Thread(target=thread_shared_1)
        thread_2 = Thread(target=thread_shared_1)
        thread_3 = Thread(target=thread_unique)
        thread_4 = Thread(target=thread_shared_2)
        thread_5 = Thread(target=thread_shared_2)

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

        # Validate order
        self.assertEqual(["shared", "shared", "shared", "shared", "unique", "unique", "shared", "shared", "shared", "shared"], exec_order)

        # Validate time
        expected_time = sleep_time * 3
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.5,
            f"Expected {expected_time}s. Got {dt}s",
        )

    def test_threads_3(self) -> None:
        """Test 1 serial thread followed by 4 parallel."""
        mutex = OrderedSharedMutex()
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

        def thread_unique():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 5)
            mutex.lock()
            increment_thread_count()
            exec_order.append("unique")
            time.sleep(sleep_time)
            exec_order.append("unique")
            mutex.unlock()
            end_times.append(time.time())

        def thread_shared():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 6)
            mutex.lock_shared()
            increment_thread_count()
            exec_order.append("shared")
            time.sleep(sleep_time)
            exec_order.append("shared")
            mutex.unlock_shared()
            end_times.append(time.time())

        thread_1 = Thread(target=thread_unique)
        thread_2 = Thread(target=thread_shared)
        thread_3 = Thread(target=thread_shared)
        thread_4 = Thread(target=thread_shared)
        thread_5 = Thread(target=thread_shared)

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

        # Validate order
        self.assertEqual(["unique", "unique", "shared", "shared", "shared", "shared", "shared", "shared", "shared", "shared"], exec_order)

        # Validate time
        expected_time = sleep_time * 2
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.5,
            f"Expected {expected_time}s. Got {dt}s",
        )

    def test_try_lock_thread_false(self) -> None:
        mutex = OrderedSharedTimedMutex()
        condition = Condition()
        end_times: list[float] = []
        thread_count = 0
        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        exec_order: list[str] = []

        try_lock_result = True
        try_lock_shared_result = True
        try_lock_for_result = True
        try_lock_until_result = True
        try_lock_shared_for_result = True
        try_lock_shared_until_result = True

        def thread_unique():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 7)
            mutex.lock()
            increment_thread_count()
            exec_order.append("unique")
            time.sleep(1)
            exec_order.append("unique")
            mutex.unlock()
            end_times.append(time.time())

        def try_lock():
            nonlocal try_lock_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_result = mutex.try_lock()
            increment_thread_count()
            if try_lock_result:
                exec_order.append("unique")
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_shared():
            nonlocal try_lock_shared_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_shared_result = mutex.try_lock_shared()
            increment_thread_count()
            if try_lock_shared_result:
                exec_order.append("shared")
                mutex.unlock_shared()
            end_times.append(time.time())

        def try_lock_for():
            nonlocal try_lock_for_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_for_result = mutex.try_lock_for(timedelta(milliseconds=500))
            increment_thread_count()
            if try_lock_for_result:
                exec_order.append("unique")
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_until():
            nonlocal try_lock_until_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_until_result = mutex.try_lock_until(
                datetime.now() + timedelta(milliseconds=500)
            )
            increment_thread_count()
            if try_lock_until_result:
                exec_order.append("unique")
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_shared_for():
            nonlocal try_lock_shared_for_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_shared_for_result = mutex.try_lock_shared_for(
                timedelta(milliseconds=500)
            )
            increment_thread_count()
            if try_lock_shared_for_result:
                exec_order.append("shared")
                mutex.unlock_shared()
            end_times.append(time.time())

        def try_lock_shared_until():
            nonlocal try_lock_shared_until_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_shared_until_result = mutex.try_lock_shared_until(
                datetime.now() + timedelta(milliseconds=500)
            )
            increment_thread_count()
            if try_lock_shared_until_result:
                exec_order.append("shared")
                mutex.unlock_shared()
            end_times.append(time.time())

        blocking_thread = Thread(target=thread_unique)
        try_lock_thread = Thread(target=try_lock)
        try_lock_shared_thread = Thread(target=try_lock_shared)
        try_lock_for_thread = Thread(target=try_lock_for)
        try_lock_until_thread = Thread(target=try_lock_until)
        try_lock_shared_for_thread = Thread(target=try_lock_shared_for)
        try_lock_shared_until_thread = Thread(target=try_lock_shared_until)

        blocking_thread.start()
        try_lock_thread.start()
        try_lock_shared_thread.start()
        try_lock_for_thread.start()
        try_lock_until_thread.start()
        try_lock_shared_for_thread.start()
        try_lock_shared_until_thread.start()

        # Wait for all threads to start
        with condition:
            condition.wait_for(lambda: thread_count >= 7)

        # Get start time
        t = time.time()

        blocking_thread.join()
        try_lock_thread.join()
        try_lock_shared_thread.join()
        try_lock_for_thread.join()
        try_lock_until_thread.join()
        try_lock_shared_for_thread.join()
        try_lock_shared_until_thread.join()

        dt = max(end_times) - t
        self.assertEqual(["unique", "unique"], exec_order)
        expected_time = 1
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.5,
            f"Expected {expected_time}s. Got {dt}s",
        )

        self.assertFalse(try_lock_result)
        self.assertFalse(try_lock_shared_result)
        self.assertFalse(try_lock_for_result)
        self.assertFalse(try_lock_until_result)
        self.assertFalse(try_lock_shared_for_result)
        self.assertFalse(try_lock_shared_until_result)

    def test_try_lock_thread_true(self) -> None:
        mutex = OrderedSharedTimedMutex()
        condition = Condition()

        exec_order: list = []
        end_times: list[float] = []
        thread_count = 0
        def increment_thread_count():
            nonlocal thread_count
            thread_count += 1
            with condition:
                condition.notify_all()

        try_lock_for_result = False
        try_lock_until_result = False
        try_lock_shared_for_result = False
        try_lock_shared_until_result = False

        def thread_unique():
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 5)
            mutex.lock()
            increment_thread_count()
            exec_order.append(1)
            time.sleep(1)
            exec_order.append(1)
            mutex.unlock()
            end_times.append(time.time())

        def try_lock_for():
            nonlocal try_lock_for_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 6)
            try_lock_for_result = mutex.try_lock_for(timedelta(seconds=2))
            increment_thread_count()
            if try_lock_for_result:
                exec_order.append(2)
                time.sleep(1)
                exec_order.append(2)
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_until():
            nonlocal try_lock_until_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count == 7)
            try_lock_until_result = mutex.try_lock_until(
                datetime.now() + timedelta(seconds=2)
            )
            increment_thread_count()
            if try_lock_until_result:
                exec_order.append(3)
                time.sleep(1)
                exec_order.append(3)
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_shared_for():
            nonlocal try_lock_shared_for_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_shared_for_result = mutex.try_lock_shared_for(timedelta(seconds=2))
            increment_thread_count()
            if try_lock_shared_for_result:
                exec_order.append("shared")
                time.sleep(1)
                exec_order.append("shared")
                mutex.unlock_shared()
            end_times.append(time.time())

        def try_lock_shared_until():
            nonlocal try_lock_shared_until_result
            increment_thread_count()
            with condition:
                condition.wait_for(lambda: thread_count >= 8)
            try_lock_shared_until_result = mutex.try_lock_shared_until(
                datetime.now() + timedelta(seconds=2)
            )
            increment_thread_count()
            if try_lock_shared_until_result:
                exec_order.append("shared")
                time.sleep(1)
                exec_order.append("shared")
                mutex.unlock_shared()
            end_times.append(time.time())

        blocking_thread = Thread(target=thread_unique)
        try_lock_for_thread = Thread(target=try_lock_for)
        try_lock_until_thread = Thread(target=try_lock_until)
        try_lock_shared_for_thread = Thread(target=try_lock_shared_for)
        try_lock_shared_until_thread = Thread(target=try_lock_shared_until)

        blocking_thread.start()
        try_lock_for_thread.start()
        try_lock_until_thread.start()
        try_lock_shared_for_thread.start()
        try_lock_shared_until_thread.start()

        # Wait for all threads to start
        with condition:
            condition.wait_for(lambda: thread_count >= 5)

        # Get start time
        t = time.time()

        blocking_thread.join()
        try_lock_for_thread.join()
        try_lock_until_thread.join()
        try_lock_shared_for_thread.join()
        try_lock_shared_until_thread.join()

        dt = max(end_times) - t
        self.assertEqual([1, 1, 2, 2, 3, 3, "shared", "shared", "shared", "shared"], exec_order)
        expected_time = 4
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.5,
            f"Expected {expected_time}s. Got {dt}s",
        )

        self.assertTrue(try_lock_for_result)
        self.assertTrue(try_lock_until_result)

    def test_cancel(self) -> None:
        """
        Two threads acquire a mutex then trying to acquire the other mutex.
        Test the cancel manager working when called before and after the second mutex lock is called.
        """
        for sleep_time in [0.1, 2.0]:
            for timeout in [False, True]:
                with self.subTest(sleep_time=sleep_time, timeout=timeout):
                    mutex_1 = OrderedSharedTimedMutex()
                    mutex_2 = OrderedSharedTimedMutex()
                    condition = Condition()

                    thread_1_result = False
                    thread_2_result = False

                    end_times: list[float] = []
                    thread_count = 0

                    def increment_thread_count():
                        nonlocal thread_count
                        thread_count += 1
                        with condition:
                            condition.notify_all()

                    def thread_1_func(cancel_manager: AbstractCancelManager):
                        nonlocal thread_1_result
                        increment_thread_count()
                        with condition:
                            condition.wait_for(lambda: thread_count >= 2)
                        mutex_1.lock(cancel_manager)
                        increment_thread_count()
                        with condition:
                            condition.wait_for(lambda: thread_count >= 4)
                        time.sleep(1)
                        if timeout:
                            locked = mutex_2.try_lock_for(
                                timedelta(seconds=10), cancel_manager
                            )
                            if locked:
                                mutex_2.unlock()
                            thread_1_result = locked
                        else:
                            try:
                                mutex_2.lock(cancel_manager)
                            except TaskCancelled:
                                pass
                            else:
                                thread_1_result = True
                                mutex_2.unlock()
                        mutex_1.unlock()
                        end_times.append(time.time())

                    def thread_2_func(cancel_manager: AbstractCancelManager):
                        nonlocal thread_2_result
                        increment_thread_count()
                        with condition:
                            condition.wait_for(lambda: thread_count >= 2)
                        mutex_2.lock(cancel_manager)
                        increment_thread_count()
                        with condition:
                            condition.wait_for(lambda: thread_count >= 4)
                        time.sleep(1)
                        if timeout:
                            locked = mutex_1.try_lock_for(
                                timedelta(seconds=10), cancel_manager
                            )
                            if locked:
                                mutex_1.unlock()
                            thread_2_result = not locked
                        else:
                            try:
                                mutex_1.lock(cancel_manager)
                            except TaskCancelled:
                                thread_2_result = True
                            else:
                                mutex_1.unlock()
                        mutex_2.unlock()
                        end_times.append(time.time())

                    cancel_manager_1 = CancelManager()
                    cancel_manager_2 = CancelManager()

                    thread_1 = Thread(target=thread_1_func, args=(cancel_manager_1,))
                    thread_2 = Thread(target=thread_2_func, args=(cancel_manager_2,))

                    thread_1.start()
                    thread_2.start()

                    # Wait for all threads to start
                    with condition:
                        condition.wait_for(lambda: thread_count >= 2)

                    # Get start time
                    t = time.time()

                    with condition:
                        condition.wait_for(lambda: thread_count >= 4)

                    # Wait for the mutexes to be locked
                    time.sleep(sleep_time)

                    # cancel the second thread
                    cancel_manager_2.cancel()

                    thread_1.join()
                    thread_2.join()

                    dt = max(end_times) - t
                    expected_time = max(1.0, sleep_time)
                    self.assertTrue(
                        expected_time - 0.01 <= dt <= expected_time + 0.5,
                        f"Expected {expected_time}s. Got {dt}s",
                    )

                    self.assertTrue(thread_1_result)
                    self.assertTrue(thread_2_result)


if __name__ == "__main__":
    unittest.main()
