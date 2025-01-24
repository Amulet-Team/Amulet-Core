# from unittest import TestCase
# import weakref
# import time
# from threading import Thread
#
# from amulet.utils.task_manager import AbstractCancelManager, CancelManager
# from amulet.utils.mutex import OrderedSharedTimedMutex, Deadlock
# from amulet.utils.lock import OrderedSharedLock, LockNotAcquired
#
#
# class LockTestCase(TestCase):
#     def test_lock_not_acquired(self) -> None:
#         self.assertTrue(issubclass(LockNotAcquired, RuntimeError))
#
#     def test_empty_constructor(self) -> None:
#         lock = OrderedSharedLock()
#         self.assertTrue(lock.acquire_unique(False))
#         lock.release_unique()
# 
#     def test_mutex_constructor(self) -> None:
#         mutex = OrderedSharedTimedMutex()
#         lock = OrderedSharedLock(mutex)
#         self.assertTrue(lock.acquire_unique(False))
#         lock.release_unique()
#
#     def test_mutex_lifespan(self) -> None:
#         mutex = OrderedSharedTimedMutex()
#         mutex_ref = weakref.ref(mutex)
#         lock = OrderedSharedLock(mutex)
#         del mutex
#         self.assertIsNotNone(mutex_ref())
#         del lock
#         self.assertIsNone(mutex_ref())
#
#     def test_unique_lifespan(self) -> None:
#         lock = OrderedSharedLock()
#         lock_ref = weakref.ref(lock)
#         unique = lock.unique()
#         del lock
#         self.assertIsNotNone(lock_ref())
#         del unique
#         self.assertIsNone(lock_ref())
#
#     def test_shared_lifespan(self) -> None:
#         lock = OrderedSharedLock()
#         lock_ref = weakref.ref(lock)
#         shared = lock.shared()
#         del lock
#         self.assertIsNotNone(lock_ref())
#         del shared
#         self.assertIsNone(lock_ref())
#
#     def test_exceptions(self) -> None:
#         lock = OrderedSharedLock()
#         with lock.unique():
#             with self.assertRaises(Deadlock):
#                 with lock.unique():
#                     pass
#             with self.assertRaises(Deadlock):
#                 with lock.shared():
#                     pass
#             with self.assertRaises(Deadlock):
#                 lock.acquire_unique(True)
#             with self.assertRaises(Deadlock):
#                 lock.acquire_unique(False)
#             with self.assertRaises(Deadlock):
#                 lock.acquire_shared(True)
#             with self.assertRaises(Deadlock):
#                 lock.acquire_shared(False)
#         with lock.shared():
#             with self.assertRaises(Deadlock):
#                 with lock.unique():
#                     pass
#             with self.assertRaises(Deadlock):
#                 with lock.shared():
#                     pass
#             with self.assertRaises(Deadlock):
#                 lock.acquire_unique(True)
#             with self.assertRaises(Deadlock):
#                 lock.acquire_unique(False)
#             with self.assertRaises(Deadlock):
#                 lock.acquire_shared(True)
#             with self.assertRaises(Deadlock):
#                 lock.acquire_shared(False)
#
#     def test_parallel(self) -> None:
#         lock = OrderedSharedLock()
#
#         sleep_time = 0.3
#
#         def parallel_func():
#             with lock.shared(timeout=5):
#                 time.sleep(sleep_time)
#
#         def serial_func():
#             with lock.unique(timeout=5):
#                 time.sleep(sleep_time)
#
#         thread_1 = Thread(target=parallel_func)
#         thread_2 = Thread(target=parallel_func)
#         thread_3 = Thread(target=serial_func)
#         thread_4 = Thread(target=parallel_func)
#         thread_5 = Thread(target=parallel_func)
#
#         t = time.time()
#
#         # Start threads
#         thread_1.start()
#         thread_2.start()
#         time.sleep(0.1)
#         thread_3.start()
#         thread_4.start()
#         thread_5.start()
#
#         # Wait for threads to finish
#         thread_1.join()
#         thread_2.join()
#         thread_3.join()
#         thread_4.join()
#         thread_5.join()
#
#         dt = time.time() - t
#
#         expected_time = sleep_time * 3
#         self.assertTrue(
#             expected_time - 0.01 <= dt <= expected_time + 0.1,
#             f"Expected {expected_time}s. Got {dt}s",
#         )
#
#     def test_timeout(self) -> None:
#         result_1 = False
#         result_2 = False
#
#         lock = OrderedSharedLock()
#
#         def func_1():
#             nonlocal result_1
#             try:
#                 with lock.unique(blocking=False):
#                     time.sleep(0.5)
#             except LockNotAcquired:
#                 result_1 = False
#             else:
#                 result_1 = True
#
#         def func_2():
#             nonlocal result_2
#             try:
#                 with lock.unique(timeout=0.1):
#                     time.sleep(0.5)
#             except LockNotAcquired:
#                 result_2 = True
#             else:
#                 result_2 = False
#
#         thread_1 = Thread(target=func_1)
#         thread_2 = Thread(target=func_2)
#
#         t = time.time()
#
#         # Start threads
#         thread_1.start()
#         time.sleep(0.1)
#         thread_2.start()
#
#         # Wait for threads to finish
#         thread_1.join()
#         thread_2.join()
#
#         dt = time.time() - t
#
#         self.assertTrue(
#             0.49 <= dt <= 0.6,
#             f"Expected 0.5s. Got {dt}s",
#         )
#
#         self.assertTrue(result_1)
#         self.assertTrue(result_2)
#
#     def test_cancel(self) -> None:
#         result_1 = False
#         result_2 = False
#
#         lock_1 = OrderedSharedLock()
#         lock_2 = OrderedSharedLock()
#
#         def func_1(cancel_manager: AbstractCancelManager):
#             nonlocal result_1
#             with lock_1.unique(blocking=False):
#                 time.sleep(0.1)
#                 with lock_2.unique(cancel_manager=cancel_manager):
#                     result_1 = True
#
#         def func_2(cancel_manager: AbstractCancelManager):
#             nonlocal result_2
#             with lock_2.unique(blocking=False):
#                 time.sleep(0.1)
#                 try:
#                     with lock_1.unique(cancel_manager=cancel_manager):
#                         pass
#                 except LockNotAcquired:
#                     result_2 = True
#
#         cancel_manager_1 = CancelManager()
#         cancel_manager_2 = CancelManager()
#
#         thread_1 = Thread(target=func_1, args=(cancel_manager_1,))
#         thread_2 = Thread(target=func_2, args=(cancel_manager_2,))
#
#         t = time.time()
#
#         # Start threads
#         thread_1.start()
#         thread_2.start()
#
#         time.sleep(0.5)
#
#         cancel_manager_2.cancel()
#
#         # Wait for threads to finish
#         thread_1.join()
#         thread_2.join()
#
#         dt = time.time() - t
#
#         self.assertTrue(
#             0.49 <= dt <= 0.6,
#             f"Expected 0.5s. Got {dt}s",
#         )
#
#         self.assertTrue(result_1)
#         self.assertTrue(result_2)
