import unittest
from datetime import timedelta, datetime
from threading import Thread, Lock, Condition
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

        def thread_shared():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            mutex.lock_shared()
            exec_order.append("shared")
            time.sleep(0.5)
            mutex.unlock_shared()
            end_times.append(time.time())

        def thread_unique():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            mutex.lock()
            exec_order.append("unique")
            time.sleep(0.5)
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
        while thread_count != 5:
            time.sleep(0.01)

        # Get start time
        t = time.time()
        # Wake all threads
        with condition:
            condition.notify_all()

        # Wait for threads to finish
        thread_1.join()
        thread_2.join()
        thread_3.join()
        thread_4.join()
        thread_5.join()

        dt = max(end_times) - t

        # validate order
        self.assertEqual(["shared", "shared", "shared", "shared", "unique"], exec_order)

        # Validate time
        self.assertTrue(0.99 <= dt <= 1.1, str(dt))

    def test_threads_2(self) -> None:
        """Test 2 threads in parallel followed by 1 serial then another 2 parallel."""
        mutex = OrderedSharedMutex()
        condition = Condition()

        exec_order: list[str] = []
        end_times: list[float] = []
        thread_count = 0

        sleep_time = 0.5

        def thread_shared_1():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            mutex.lock_shared()
            exec_order.append("shared")
            time.sleep(sleep_time)
            mutex.unlock_shared()
            end_times.append(time.time())

        def thread_unique():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            mutex.lock()
            exec_order.append("unique")
            time.sleep(sleep_time)
            mutex.unlock()
            end_times.append(time.time())

        def thread_shared_2():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.2)
            mutex.lock_shared()
            exec_order.append("shared")
            time.sleep(sleep_time)
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
        while thread_count != 5:
            time.sleep(0.01)

        # Get start time
        t = time.time()
        # Wake all threads
        with condition:
            condition.notify_all()

        # Wait for threads to finish
        thread_1.join()
        thread_2.join()
        thread_3.join()
        thread_4.join()
        thread_5.join()

        dt = max(end_times) - t

        # Validate order
        self.assertEqual(["shared", "shared", "unique", "shared", "shared"], exec_order)

        # Validate time
        expected_time = sleep_time * 3
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.1,
            f"Expected {expected_time}s. Got {dt}s",
        )

    def test_threads_3(self) -> None:
        """Test 1 serial thread followed by 4 parallel."""
        mutex = OrderedSharedMutex()
        condition = Condition()

        exec_order: list[str] = []
        end_times: list[float] = []
        thread_count = 0

        sleep_time = 0.5

        def thread_unique():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            mutex.lock()
            exec_order.append("unique")
            time.sleep(sleep_time)
            mutex.unlock()
            end_times.append(time.time())

        def thread_shared():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            mutex.lock_shared()
            exec_order.append("shared")
            time.sleep(sleep_time)
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
        while thread_count != 5:
            time.sleep(0.01)

        # Get start time
        t = time.time()
        # Wake all threads
        with condition:
            condition.notify_all()

        # Wait for threads to finish
        thread_1.join()
        thread_2.join()
        thread_3.join()
        thread_4.join()
        thread_5.join()

        dt = max(end_times) - t

        # Validate order
        self.assertEqual(["unique", "shared", "shared", "shared", "shared"], exec_order)

        # Validate time
        expected_time = sleep_time * 2
        self.assertTrue(
            expected_time - 0.01 <= dt <= expected_time + 0.1,
            f"Expected {expected_time}s. Got {dt}s",
        )

    def test_try_lock_thread_false(self) -> None:
        mutex = OrderedSharedTimedMutex()
        condition = Condition()
        end_times: list[float] = []
        thread_count = 0

        exec_order: list[str] = []

        try_lock_result = True
        try_lock_shared_result = True
        try_lock_for_result = True
        try_lock_until_result = True
        try_lock_shared_for_result = True
        try_lock_shared_until_result = True

        def thread_unique():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            mutex.lock()
            time.sleep(1)
            exec_order.append("unique")
            mutex.unlock()
            end_times.append(time.time())

        def try_lock():
            nonlocal thread_count, try_lock_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            try_lock_result = mutex.try_lock()
            if try_lock_result:
                exec_order.append("unique")
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_shared():
            nonlocal thread_count, try_lock_shared_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            try_lock_shared_result = mutex.try_lock_shared()
            if try_lock_shared_result:
                exec_order.append("shared")
                mutex.unlock_shared()
            end_times.append(time.time())

        def try_lock_for():
            nonlocal thread_count, try_lock_for_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            try_lock_for_result = mutex.try_lock_for(timedelta(milliseconds=500))
            if try_lock_for_result:
                exec_order.append("unique")
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_until():
            nonlocal thread_count, try_lock_until_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            try_lock_until_result = mutex.try_lock_until(
                datetime.now() + timedelta(milliseconds=500)
            )
            if try_lock_until_result:
                exec_order.append("unique")
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_shared_for():
            nonlocal thread_count, try_lock_shared_for_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            try_lock_shared_for_result = mutex.try_lock_shared_for(
                timedelta(milliseconds=500)
            )
            if try_lock_shared_for_result:
                exec_order.append("shared")
                mutex.unlock_shared()
            end_times.append(time.time())

        def try_lock_shared_until():
            nonlocal thread_count, try_lock_shared_until_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            try_lock_shared_until_result = mutex.try_lock_shared_until(
                datetime.now() + timedelta(milliseconds=500)
            )
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
        while thread_count != 7:
            time.sleep(0.01)

        # Get start time
        t = time.time()
        # Wake all threads
        with condition:
            condition.notify_all()

        blocking_thread.join()
        try_lock_thread.join()
        try_lock_shared_thread.join()
        try_lock_for_thread.join()
        try_lock_until_thread.join()
        try_lock_shared_for_thread.join()
        try_lock_shared_until_thread.join()

        dt = max(end_times) - t
        self.assertEqual(["unique"], exec_order)
        self.assertTrue(0.99 <= dt <= 1.2, f"Expected 1s. Got {dt}s")

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

        try_lock_for_result = False
        try_lock_until_result = False
        try_lock_shared_for_result = False
        try_lock_shared_until_result = False

        def thread_unique():
            nonlocal thread_count
            with condition:
                thread_count += 1
                condition.wait()
            mutex.lock()
            time.sleep(0.5)
            exec_order.append(1)
            mutex.unlock()
            end_times.append(time.time())

        def try_lock_for():
            nonlocal thread_count, try_lock_for_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.1)
            try_lock_for_result = mutex.try_lock_for(timedelta(seconds=2))
            if try_lock_for_result:
                exec_order.append(2)
                time.sleep(0.5)
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_until():
            nonlocal thread_count, try_lock_until_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.2)
            try_lock_until_result = mutex.try_lock_until(
                datetime.now() + timedelta(seconds=2)
            )
            if try_lock_until_result:
                exec_order.append(3)
                time.sleep(0.5)
                mutex.unlock()
            end_times.append(time.time())

        def try_lock_shared_for():
            nonlocal thread_count, try_lock_shared_for_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.3)
            try_lock_shared_for_result = mutex.try_lock_shared_for(timedelta(seconds=2))
            if try_lock_shared_for_result:
                exec_order.append("shared")
                time.sleep(0.5)
                mutex.unlock_shared()
            end_times.append(time.time())

        def try_lock_shared_until():
            nonlocal thread_count, try_lock_shared_until_result
            with condition:
                thread_count += 1
                condition.wait()
            time.sleep(0.4)
            try_lock_shared_until_result = mutex.try_lock_shared_until(
                datetime.now() + timedelta(seconds=2)
            )
            if try_lock_shared_until_result:
                exec_order.append("shared")
                time.sleep(0.5)
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
        while thread_count != 5:
            time.sleep(0.01)

        # Get start time
        t = time.time()
        # Wake all threads
        with condition:
            condition.notify_all()

        blocking_thread.join()
        try_lock_for_thread.join()
        try_lock_until_thread.join()
        try_lock_shared_for_thread.join()
        try_lock_shared_until_thread.join()

        dt = max(end_times) - t
        self.assertEqual([1, 2, 3, "shared", "shared"], exec_order)
        self.assertTrue(1.99 <= dt <= 2.2, f"Expected 2s. Got {dt}s")

        self.assertTrue(try_lock_for_result)
        self.assertTrue(try_lock_until_result)

    def test_cancel(self) -> None:
        """
        Two threads acquire a mutex then trying to acquire the other mutex.
        Test the cancel manager working when called before and after the second mutex lock is called.
        """
        for sleep_time in [0.1, 1.0]:
            for timeout in [False, True]:
                with self.subTest(sleep_time=sleep_time, timeout=timeout):
                    mutex_1 = OrderedSharedTimedMutex()
                    mutex_2 = OrderedSharedTimedMutex()
                    condition = Condition()

                    thread_1_result = False
                    thread_2_result = False

                    end_times: list[float] = []
                    thread_count = 0

                    def thread_1_func(cancel_manager: AbstractCancelManager):
                        nonlocal thread_count, thread_1_result
                        with condition:
                            thread_count += 1
                            condition.wait()
                        mutex_1.lock(cancel_manager)
                        time.sleep(0.5)
                        if timeout:
                            locked = mutex_2.try_lock_for(
                                timedelta(seconds=1), cancel_manager
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
                        nonlocal thread_count, thread_2_result
                        with condition:
                            thread_count += 1
                            condition.wait()
                        mutex_2.lock(cancel_manager)
                        time.sleep(0.5)
                        if timeout:
                            locked = mutex_1.try_lock_for(
                                timedelta(seconds=1), cancel_manager
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
                    while thread_count != 2:
                        time.sleep(0.01)

                    # Get start time
                    t = time.time()
                    # Wake all threads
                    with condition:
                        condition.notify_all()

                    # Wait for the mutexes to be locked
                    time.sleep(sleep_time)

                    # cancel the second thread
                    cancel_manager_2.cancel()

                    thread_1.join()
                    thread_2.join()

                    dt = max(end_times) - t
                    expected_time = max(0.5, sleep_time)
                    self.assertTrue(
                        expected_time - 0.01 <= dt <= expected_time + 0.2,
                        f"Expected {expected_time}s. Got {dt}s",
                    )

                    self.assertTrue(thread_1_result)
                    self.assertTrue(thread_2_result)


if __name__ == "__main__":
    unittest.main()
