from typing import Callable, Iterator
from threading import Lock, Condition, get_ident
from contextlib import contextmanager
import time
import logging

from .task_manager import AbstractCancelManager, VoidCancelManager, TaskCancelled


log = logging.getLogger(__name__)


class LockNotAcquired(TaskCancelled):
    """An exception raised if the lock was not acquired."""


class ShareableRLock:
    """
    This is a custom lock implementation that can be acquired in
    1) unique mode.
        - This is the normal mode where only this thread can use the resource.
        - All other acquires block until this releases it.
    2) shared mode.
        - This allows multiple threads to acquire the resource at the same time.
        - This is useful if multiple threads want to read a resource but not write to it.
        - If the resource is locked in unique mode this will block
        - Once locked in shared mode it

    """

    _state_lock: Lock
    _state_condition: Condition
    _blocking_threads: dict[
        int, tuple[bool, bool]
    ]  # dict[thread_id, tuple[is_serial, is_blocking]]
    _unique_thread: int | None
    _unique_r_count: int
    _shared_threads: dict[
        int, int
    ]  # Map from thread id to the number of times it has been acquired in shared mode.

    def __init__(self) -> None:
        self._state_lock = Lock()
        self._state_condition = Condition(self._state_lock)
        self._blocking_threads = {}
        self._unique_thread = None
        self._unique_r_count = 0
        self._shared_threads = {}

    def _wait(
        self,
        exit_condition: Callable[[], bool],
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
    ) -> bool:
        """Wait until a condition is False.

        :param exit_condition: The condition to check.
        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: True if the lock was acquired, otherwise False.
        """
        if task_manager.is_cancel_requested():
            return False

        if exit_condition():
            # We don't need to wait
            return True

        if not blocking:
            # Need to wait but told not to
            return False

        if timeout == -1:
            # wait with no timeout
            while not exit_condition():
                if task_manager.is_cancel_requested():
                    return False
                self._state_condition.wait()
            return True

        else:
            # Wait with a timeout
            end_time = time.time() + timeout
            while not exit_condition():
                if task_manager.is_cancel_requested():
                    return False
                wait_time = end_time - time.time()
                if wait_time > 0:
                    self._state_condition.wait(wait_time)
                else:
                    return False
            return True

    def acquire_unique(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
    ) -> bool:
        """
        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        Acquire the lock in unique mode. This is equivalent to threading.RLock.acquire
        With improper use this can lead to a deadlock.
        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: True if the lock was acquired otherwise False.
        """
        with self._state_lock:
            ident = get_ident()
            if (
                ident in self._shared_threads
                and blocking
                and timeout == -1
                and any(
                    self._blocking_threads[thread_id][1]
                    for thread_id in self._blocking_threads
                    if thread_id in self._shared_threads
                )
            ):
                logging.warning("Possible deadlock")

            def on_cancel() -> None:
                with self._state_lock:
                    self._state_condition.notify_all()

            task_manager.register_on_cancel(on_cancel)

            self._blocking_threads[ident] = (
                True,
                blocking
                and timeout == -1
                and isinstance(task_manager, VoidCancelManager),
            )

            def exit_condition() -> bool:
                # The thread was the first to join
                # The lock is not locked or is locked by this thread
                can_exit = (
                    next(iter(self._blocking_threads)) == ident
                    and self._unique_thread in (None, ident)
                    and self._shared_threads.keys() in (set(), {ident})
                )
                if can_exit:
                    self._blocking_threads.pop(ident)
                return can_exit

            locked = self._wait(
                exit_condition,
                blocking,
                timeout,
                task_manager,
            )

            task_manager.unregister_on_cancel(on_cancel)

            if locked:
                # Lock it
                self._unique_thread = ident
                self._unique_r_count += 1
                return True
            else:
                self._blocking_threads.pop(ident)
                return False

    def release_unique(self) -> None:
        """
        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        Release the unique hold on the lock. This must be called by the same thread that acquired it.
        This must be called exactly the same number of times as :meth:`acquire_unique` was called.
        """
        with self._state_lock:
            if self._unique_thread != get_ident():
                raise RuntimeError("Lock released by a thread that does not own it.")

            self._unique_r_count -= 1
            if self._unique_r_count == 0:
                self._unique_thread = None
                # Let another thread continue
                self._state_condition.notify_all()

    def acquire_shared(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
    ) -> bool:
        """
        Only use this if you know what you are doing. Consider using :meth:`shared` instead
        Acquire the lock in shared mode.
        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: True if the lock was acquired otherwise False.
        """
        with self._state_lock:
            ident = get_ident()

            def exit_condition() -> bool:
                if self._unique_thread == ident or ident in self._shared_threads:
                    # Lock is already acquired by this thread
                    self._blocking_threads.pop(ident)
                    return True
                elif self._unique_thread is None:
                    # Is it not locked in unique mode
                    for thread_id, (is_serial, _) in self._blocking_threads.items():
                        if is_serial:
                            return False
                        elif thread_id == ident:
                            self._blocking_threads.pop(ident)
                            return True
                return False

            def on_cancel() -> None:
                with self._state_lock:
                    self._state_condition.notify_all()

            task_manager.register_on_cancel(on_cancel)

            self._blocking_threads[ident] = (False, False)

            locked = self._wait(exit_condition, blocking, timeout, task_manager)

            task_manager.unregister_on_cancel(on_cancel)

            if locked:
                # Not unique locked or unique locked by the current thread
                self._shared_threads.setdefault(ident, 0)
                self._shared_threads[ident] += 1
                return True
            else:
                self._blocking_threads.pop(ident)
                return False

    def release_shared(self) -> None:
        """
        Only use this if you know what you are doing. Consider using :meth:`shared` instead
        Release the shared hold on the lock. This must be called by the same thread that acquired it.
        This must be called exactly the same number of times as :meth:`acquire_shared` was called.
        """
        with self._state_lock:
            ident = get_ident()
            if ident not in self._shared_threads:
                raise RuntimeError("Lock released by a thread that does not own it.")

            self._shared_threads[ident] -= 1
            if self._shared_threads[ident] == 0:
                self._shared_threads.pop(ident)
                self._state_condition.notify_all()

    @contextmanager
    def unique(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
    ) -> Iterator[None]:
        """
        Acquire the lock in unique mode.
        This is used as follows

        >>> lock: ShareableRLock
        >>> with lock.unique():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        This will block while all other threads using the resource finish
        and once acquired block all other threads until the lock is released.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: None
        :raises: LockNotAcquired if the lock could not be acquired.
        """
        if not self.acquire_unique(blocking, timeout, task_manager):
            raise LockNotAcquired
        try:
            yield
        finally:
            self.release_unique()

    @contextmanager
    def shared(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
    ) -> Iterator[None]:
        """
        Acquire the lock in shared mode.
        This is used as follows

        >>> lock: ShareableRLock
        >>> with lock.shared():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        If the lock is acquired by a different thread in unique mode then this will block until it is finished.
        If the lock is acquired in unique mode by this thread or by otherthreads in shared mode then this will acquire
        the lock.

        If another thread wants to acquire the lock in unique mode it will block until all threads have finished in
        shared mode.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: None
        :raises: LockNotAcquired if the lock could not be acquired.
        """
        if not self.acquire_shared(blocking, timeout, task_manager):
            raise LockNotAcquired
        try:
            yield
        finally:
            self.release_shared()
