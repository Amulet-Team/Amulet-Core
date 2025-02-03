from unittest import TestCase
import weakref
import time
from threading import Thread, Condition
from typing import Callable, Any
from contextlib import AbstractContextManager, suppress
from enum import Enum
import itertools
import sys

from amulet.utils.task_manager import AbstractCancelManager, CancelManager
from amulet.utils.lock import (
    Deadlock,
    OrderedLock,
    LockNotAcquired,
    Lock,
    RLock,
    SharedLock,
)


class ThreadStepManager:
    def __init__(self):
        self.condition = Condition()
        self.step = 0

    def increment(self) -> None:
        with self.condition:
            self.step += 1
            self.condition.notify_all()

    def wait(self, step_min: int) -> None:
        with self.condition:
            self.condition.wait_for(lambda: step_min <= self.step)


class Abstract:
    class LockTestCase(TestCase):
        def _ab_thread_test(
            self,
            a: Callable[[ThreadStepManager, list], None],
            b: Callable[[ThreadStepManager, list], None],
            expected_order: list,
            expected_time: float,
        ) -> None:
            step = ThreadStepManager()
            exec_order: list = []
            end_times: list[float] = []

            def f1():
                step.increment()
                step.wait(3)
                a(step, exec_order)
                end_times.append(time.time())

            def f2():
                step.increment()
                step.wait(4)
                b(step, exec_order)
                end_times.append(time.time())

            thread_1 = Thread(target=f1)
            thread_2 = Thread(target=f2)

            thread_1.start()
            thread_2.start()

            step.wait(2)
            t = time.time()
            step.increment()

            thread_1.join()
            thread_2.join()

            self.assertEqual(expected_order, exec_order)

            dt = max(end_times) - t
            self.assertTrue(
                expected_time - 0.01 <= dt <= expected_time + 0.5,
                f"Expected {expected_time}s. Got {dt}s",
            )


# MacOS runners
# SLEEP_TIME = 0.5 if sys.platform == "darwin" else 0.1
SLEEP_TIME = 0.1


class LockTestCase(Abstract.LockTestCase):
    def test_lock(self) -> None:
        lock = Lock()
        with lock:
            self.assertTrue(True)

    def test_parallel(self) -> None:
        lock = Lock()

        def ctx(v: int):
            def f(step: ThreadStepManager, exec_order: list):
                with lock:
                    step.increment()
                    exec_order.append(v)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v + 1)

            return f

        def raw(blocking: bool, v: int):
            def f(step: ThreadStepManager, exec_order: list):
                if lock.acquire(blocking):
                    step.increment()
                    exec_order.append(v)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v + 1)
                    lock.release()

            return f

        with self.subTest():
            self._ab_thread_test(ctx(1), ctx(3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(ctx(1), raw(False, 3), [1, 2], SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(ctx(1), raw(True, 3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(raw(False, 1), ctx(3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(raw(False, 1), raw(False, 3), [1, 2], SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(
                raw(False, 1), raw(True, 3), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(raw(True, 1), ctx(3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(raw(True, 1), raw(False, 3), [1, 2], SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(
                raw(True, 1), raw(True, 3), [1, 2, 3, 4], 2 * SLEEP_TIME
            )


class RLockTestCase(Abstract.LockTestCase):
    def test_rlock(self) -> None:
        lock = RLock()
        with lock:
            with lock:
                self.assertTrue(True)

    def test_parallel(self) -> None:
        lock = RLock()

        def ctx(v: int):
            def f(step: ThreadStepManager, exec_order: list):
                with lock:
                    step.increment()
                    exec_order.append(v)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v + 1)

            return f

        def raw(blocking: bool, v: int):
            def f(step: ThreadStepManager, exec_order: list):
                if lock.acquire(blocking):
                    step.increment()
                    exec_order.append(v)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v + 1)
                    lock.release()

            return f

        with self.subTest():
            self._ab_thread_test(ctx(1), ctx(3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(ctx(1), raw(False, 3), [1, 2], SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(ctx(1), raw(True, 3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(raw(False, 1), ctx(3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(raw(False, 1), raw(False, 3), [1, 2], SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(
                raw(False, 1), raw(True, 3), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(raw(True, 1), ctx(3), [1, 2, 3, 4], 2 * SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(raw(True, 1), raw(False, 3), [1, 2], SLEEP_TIME)
        with self.subTest():
            self._ab_thread_test(
                raw(True, 1), raw(True, 3), [1, 2, 3, 4], 2 * SLEEP_TIME
            )


class SharedLockTestCase(Abstract.LockTestCase):
    def test_shared_lock(self) -> None:
        lock = SharedLock()
        lock.acquire_unique()
        lock.release_unique()
        lock.acquire_shared()
        lock.release_shared()
        with lock.unique():
            pass
        with lock.shared():
            pass

    def test_unique_lifespan(self) -> None:
        lock = SharedLock()
        lock_ref = weakref.ref(lock)
        unique = lock.unique()
        del lock
        self.assertIsNotNone(lock_ref())
        del unique
        self.assertIsNone(lock_ref())

    def test_shared_lifespan(self) -> None:
        lock = SharedLock()
        lock_ref = weakref.ref(lock)
        shared = lock.shared()
        del lock
        self.assertIsNotNone(lock_ref())
        del shared
        self.assertIsNone(lock_ref())

    def test_parallel(self) -> None:
        lock = SharedLock()

        def ctx(shared: bool, v1: Any, v2: Any):
            def f(step: ThreadStepManager, exec_order: list):
                if shared:
                    mgr = lock.shared()
                else:
                    mgr = lock.unique()
                with mgr:
                    step.increment()
                    exec_order.append(v1)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v2)

            return f

        def raw(shared: bool, blocking: bool, v1: Any, v2: Any):
            def f(step: ThreadStepManager, exec_order: list):
                if shared:
                    locked = lock.acquire_shared(blocking)
                else:
                    locked = lock.acquire_unique(blocking)
                if locked:
                    step.increment()
                    exec_order.append(v1)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v2)
                    if shared:
                        lock.release_shared()
                    else:
                        lock.release_unique()

            return f

        with self.subTest():
            self._ab_thread_test(
                ctx(False, 1, 2), ctx(False, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(False, 1, 2), raw(False, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(False, 1, 2), raw(False, True, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, False, 1, 2), ctx(False, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, False, 1, 2), raw(False, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, False, 1, 2),
                raw(False, True, 3, 4),
                [1, 2, 3, 4],
                2 * SLEEP_TIME,
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, True, 1, 2), ctx(False, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, True, 1, 2), raw(False, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, True, 1, 2),
                raw(False, True, 3, 4),
                [1, 2, 3, 4],
                2 * SLEEP_TIME,
            )

        with self.subTest():
            self._ab_thread_test(
                ctx(False, 1, 2), ctx(True, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(False, 1, 2), raw(True, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(False, 1, 2), raw(True, True, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, False, 1, 2), ctx(True, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, False, 1, 2), raw(True, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, False, 1, 2),
                raw(True, True, 3, 4),
                [1, 2, 3, 4],
                2 * SLEEP_TIME,
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, True, 1, 2), ctx(True, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, True, 1, 2), raw(True, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(False, True, 1, 2),
                raw(True, True, 3, 4),
                [1, 2, 3, 4],
                2 * SLEEP_TIME,
            )

        with self.subTest():
            self._ab_thread_test(
                ctx(True, 1, 2), ctx(False, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(True, 1, 2), raw(False, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(True, 1, 2), raw(False, True, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, False, 1, 2), ctx(False, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, False, 1, 2), raw(False, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, False, 1, 2),
                raw(False, True, 3, 4),
                [1, 2, 3, 4],
                2 * SLEEP_TIME,
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, True, 1, 2), ctx(False, 3, 4), [1, 2, 3, 4], 2 * SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, True, 1, 2), raw(False, False, 3, 4), [1, 2], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, True, 1, 2),
                raw(False, True, 3, 4),
                [1, 2, 3, 4],
                2 * SLEEP_TIME,
            )

        with self.subTest():
            self._ab_thread_test(
                ctx(True, 0, 0), ctx(True, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(True, 0, 0), raw(True, False, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                ctx(True, 0, 0), raw(True, True, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, False, 0, 0), ctx(True, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, False, 0, 0), raw(True, False, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, False, 0, 0), raw(True, True, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, True, 0, 0), ctx(True, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, True, 0, 0), raw(True, False, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )
        with self.subTest():
            self._ab_thread_test(
                raw(True, True, 0, 0), raw(True, True, 0, 0), [0, 0, 0, 0], SLEEP_TIME
            )


class LockMode(Enum):
    Unique = "Unique"
    SharedReadOnly = "SharedReadOnly"
    SharedRead = "SharedRead"
    SharedReadWrite = "SharedReadWrite"


class OrderedLockTestCase(Abstract.LockTestCase):
    def test_lock_not_acquired(self) -> None:
        self.assertTrue(issubclass(LockNotAcquired, RuntimeError))
        with self.assertRaises(RuntimeError):
            raise LockNotAcquired
        with self.assertRaises(LockNotAcquired):
            raise LockNotAcquired

    def test_constructor(self) -> None:
        lock = OrderedLock()
        self.assertTrue(lock.acquire_unique(False))
        lock.release_unique()

    def test_unique_lifespan(self) -> None:
        lock = OrderedLock()
        lock_ref = weakref.ref(lock)
        cancel = CancelManager()
        cancel_ref = weakref.ref(cancel)
        unique = lock.unique(cancel_manager=cancel)
        del lock
        del cancel
        self.assertIsNotNone(lock_ref())
        self.assertIsNotNone(cancel_ref())
        del unique
        self.assertIsNone(lock_ref())
        self.assertIsNone(cancel_ref())

    def test_shared_lifespan(self) -> None:
        lock = OrderedLock()
        lock_ref = weakref.ref(lock)
        cancel = CancelManager()
        cancel_ref = weakref.ref(cancel)
        shared = lock.shared_read_only(cancel_manager=cancel)
        del lock
        del cancel
        self.assertIsNotNone(lock_ref())
        self.assertIsNotNone(cancel_ref())
        del shared
        self.assertIsNone(lock_ref())
        self.assertIsNone(cancel_ref())

    def test_deadlock(self) -> None:
        lock = OrderedLock()

        def lock_all():
            for blocking in (True, False):
                for timeout in (-1.0, 1.0):
                    f1: Callable[[bool, float], bool]
                    for f1 in (
                        lock.acquire_unique,
                        lock.acquire_shared_read_only,
                        lock.acquire_shared_read,
                        lock.acquire_shared_read_write,
                    ):
                        with (
                            self.subTest(blocking=blocking, timeout=timeout, func=f1),
                            self.assertRaises(Deadlock),
                        ):
                            f1(blocking, timeout)
                    f2: Callable[[bool, float], AbstractContextManager[None]]
                    for f2 in (
                        lock.unique,
                        lock.shared_read_only,
                        lock.shared_read,
                        lock.shared_read_write,
                    ):
                        with (
                            self.subTest(blocking=blocking, timeout=timeout, func=f2),
                            self.assertRaises(Deadlock),
                        ):
                            with f2(blocking, timeout):
                                pass

        with lock.unique():
            lock_all()
        with lock.shared_read_only():
            lock_all()
        with lock.shared_read():
            lock_all()
        with lock.shared_read_write():
            lock_all()

    def test_parallel(self) -> None:
        lock = OrderedLock()

        def ctx(mode: LockMode, blocking: bool, v1: Any, v2: Any):
            def f(step: ThreadStepManager, exec_order: list):
                if mode == LockMode.Unique:
                    mgr = lock.unique(blocking)
                elif mode == LockMode.SharedReadOnly:
                    mgr = lock.shared_read_only(blocking)
                elif mode == LockMode.SharedRead:
                    mgr = lock.shared_read(blocking)
                elif mode == LockMode.SharedReadWrite:
                    mgr = lock.shared_read_write(blocking)
                else:
                    raise RuntimeError

                with suppress(LockNotAcquired), mgr:
                    step.increment()
                    exec_order.append(v1)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v2)

            return f

        def raw(mode: LockMode, blocking: bool, v1: Any, v2: Any):
            def f(step: ThreadStepManager, exec_order: list):
                if mode == LockMode.Unique:
                    locked = lock.acquire_unique(blocking)
                elif mode == LockMode.SharedReadOnly:
                    locked = lock.acquire_shared_read_only(blocking)
                elif mode == LockMode.SharedRead:
                    locked = lock.acquire_shared_read(blocking)
                elif mode == LockMode.SharedReadWrite:
                    locked = lock.acquire_shared_read_write(blocking)
                else:
                    raise RuntimeError

                if locked:
                    step.increment()
                    exec_order.append(v1)
                    time.sleep(SLEEP_TIME)
                    exec_order.append(v2)
                    if mode == LockMode.Unique:
                        lock.release_unique()
                    else:
                        lock.release_shared()

            return f

        for mode_1, mode_2 in itertools.product(
            (
                LockMode.Unique,
                LockMode.SharedReadOnly,
                LockMode.SharedRead,
                LockMode.SharedReadWrite,
            ),
            repeat=2,
        ):
            for f1, f2 in itertools.product((ctx, raw), repeat=2):
                for blocking_1, blocking_2 in itertools.product(
                    (False, True), repeat=2
                ):
                    with self.subTest(
                        mode_1=mode_1,
                        mode_2=mode_2,
                        f1=f1,
                        blocking_1=blocking_1,
                        f2=f2,
                        blocking_2=blocking_2,
                    ):
                        if (
                            (
                                mode_1 == LockMode.SharedReadOnly
                                and (
                                    mode_2
                                    in [LockMode.SharedReadOnly, LockMode.SharedRead]
                                )
                            )
                            or (
                                mode_1 == LockMode.SharedRead
                                and (
                                    mode_2
                                    in [
                                        LockMode.SharedReadOnly,
                                        LockMode.SharedRead,
                                        LockMode.SharedReadWrite,
                                    ]
                                )
                            )
                            or (
                                mode_1 == LockMode.SharedReadWrite
                                and (
                                    mode_2
                                    in [LockMode.SharedRead, LockMode.SharedReadWrite]
                                )
                            )
                        ):
                            # parallel
                            self._ab_thread_test(
                                f1(mode_1, blocking_1, 0, 0),
                                f2(mode_2, blocking_2, 0, 0),
                                [0, 0, 0, 0],
                                SLEEP_TIME,
                            )
                        else:
                            # serial
                            if blocking_2:
                                self._ab_thread_test(
                                    f1(mode_1, blocking_1, 1, 2),
                                    f2(mode_2, blocking_2, 3, 4),
                                    [1, 2, 3, 4],
                                    2 * SLEEP_TIME,
                                )
                            else:
                                self._ab_thread_test(
                                    f1(mode_1, blocking_1, 1, 2),
                                    f2(mode_2, blocking_2, 3, 4),
                                    [1, 2],
                                    SLEEP_TIME,
                                )

    def test_parallel_group(self) -> None:
        lock = OrderedLock()
        step = ThreadStepManager()

        exec_order: list[str] = []
        end_times: list[float] = []

        sleep_time = 1

        def parallel_func_1():
            step.increment()
            step.wait(6)
            with lock.shared_read_only(timeout=5):
                step.increment()
                exec_order.append("shared")
                time.sleep(sleep_time)
                exec_order.append("shared")
            end_times.append(time.time())

        def serial_func():
            step.increment()
            step.wait(8)
            with lock.unique(timeout=5):
                step.increment()
                exec_order.append("unique")
                time.sleep(sleep_time)
                exec_order.append("unique")
            end_times.append(time.time())

        def parallel_func_2():
            step.increment()
            step.wait(9)
            with lock.shared_read_only(timeout=5):
                step.increment()
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
        step.wait(5)
        # Get start time
        t = time.time()
        step.increment()

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
        for raw in (False, True):
            for mode in (
                LockMode.Unique,
                LockMode.SharedReadOnly,
                LockMode.SharedRead,
                LockMode.SharedReadWrite,
            ):
                with self.subTest(raw=raw, mode=mode):
                    result_1 = False
                    result_2 = False

                    lock = OrderedLock()
                    step = ThreadStepManager()

                    end_times: list[float] = []

                    def func_1():
                        nonlocal result_1
                        step.increment()
                        step.wait(3)
                        try:
                            with lock.unique(blocking=False):
                                step.increment()
                                time.sleep(1)
                        except LockNotAcquired:
                            result_1 = False
                        else:
                            result_1 = True
                        end_times.append(time.time())

                    def func_2():
                        nonlocal result_2
                        step.increment()
                        step.wait(4)

                        if raw:
                            if mode == LockMode.Unique:
                                f = lock.acquire_unique
                            elif mode == LockMode.SharedReadOnly:
                                f = lock.acquire_shared_read_only
                            elif mode == LockMode.SharedRead:
                                f = lock.acquire_shared_read
                            elif mode == LockMode.SharedReadWrite:
                                f = lock.acquire_shared_read_write
                            else:
                                raise RuntimeError
                            if f(timeout=0.1):
                                if mode == LockMode.Unique:
                                    lock.release_unique()
                                else:
                                    lock.release_shared()
                            else:
                                result_2 = True
                        else:
                            if mode == LockMode.Unique:
                                mgr = lock.unique
                            elif mode == LockMode.SharedReadOnly:
                                mgr = lock.shared_read_only
                            elif mode == LockMode.SharedRead:
                                mgr = lock.shared_read
                            elif mode == LockMode.SharedReadWrite:
                                mgr = lock.shared_read_write
                            else:
                                raise RuntimeError
                            try:
                                with mgr(timeout=0.1):
                                    pass
                            except LockNotAcquired:
                                result_2 = True
                        end_times.append(time.time())

                    thread_1 = Thread(target=func_1)
                    thread_2 = Thread(target=func_2)

                    # Start threads
                    thread_1.start()
                    thread_2.start()

                    # Wait for all threads to start
                    step.wait(2)
                    # Get start time
                    t = time.time()
                    step.increment()

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
            for raw in (False, True):
                for mode in (
                    LockMode.Unique,
                    LockMode.SharedReadOnly,
                    LockMode.SharedRead,
                    LockMode.SharedReadWrite,
                ):
                    with self.subTest(timeout=timeout, raw=raw, mode=mode):
                        result_1 = False
                        result_2 = False

                        lock_1 = OrderedLock()
                        lock_2 = OrderedLock()

                        step = ThreadStepManager()
                        end_times: list[float] = []

                        def func_1():
                            nonlocal result_1
                            step.increment()
                            step.wait(3)
                            with lock_1.unique():
                                step.increment()
                                step.wait(5)
                                with lock_2.unique():
                                    result_1 = True
                            end_times.append(time.time())

                        def func_2(cancel_manager: AbstractCancelManager):
                            nonlocal result_2
                            step.increment()
                            step.wait(3)
                            with lock_2.unique():
                                step.increment()
                                step.wait(5)
                                time.sleep(1)
                                if raw:
                                    if mode == LockMode.Unique:
                                        f = lock_1.acquire_unique
                                    elif mode == LockMode.SharedReadOnly:
                                        f = lock_1.acquire_shared_read_only
                                    elif mode == LockMode.SharedRead:
                                        f = lock_1.acquire_shared_read
                                    elif mode == LockMode.SharedReadWrite:
                                        f = lock_1.acquire_shared_read_write
                                    else:
                                        raise RuntimeError
                                    if f(
                                        cancel_manager=cancel_manager, timeout=timeout
                                    ):
                                        if mode == LockMode.Unique:
                                            lock_1.release_unique()
                                        else:
                                            lock_1.release_shared()
                                    else:
                                        result_2 = True
                                else:
                                    if mode == LockMode.Unique:
                                        mgr = lock_1.unique
                                    elif mode == LockMode.SharedReadOnly:
                                        mgr = lock_1.shared_read_only
                                    elif mode == LockMode.SharedRead:
                                        mgr = lock_1.shared_read
                                    elif mode == LockMode.SharedReadWrite:
                                        mgr = lock_1.shared_read_write
                                    else:
                                        raise RuntimeError
                                    try:
                                        with mgr(
                                            cancel_manager=cancel_manager,
                                            timeout=timeout,
                                        ):
                                            pass
                                    except LockNotAcquired:
                                        result_2 = True
                            end_times.append(time.time())

                        cancel_manager_2 = CancelManager()

                        thread_1 = Thread(target=func_1)
                        thread_2 = Thread(target=func_2, args=(cancel_manager_2,))

                        # Start threads
                        thread_1.start()
                        thread_2.start()

                        # Wait for all threads to start
                        step.wait(2)
                        # Get start time
                        t = time.time()
                        step.increment()

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
                            f"Expected 2s. Got {dt}s",
                        )
