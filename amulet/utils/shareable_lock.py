from typing import Callable, Iterator
from threading import Lock, Condition, get_ident
from contextlib import contextmanager
import time
import logging

from .task_manager import AbstractCancelManager, VoidCancelManager


log = logging.getLogger(__name__)


class LockNotAcquired(Exception):
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
    _unique_waiting_blocking_threads: set[int]
    _unique_waiting_count: int
    _unique_thread: int | None
    _unique_count: int
    _shared_threads: dict[int, int]

    def __init__(self) -> None:
        self._state_lock = Lock()
        self._state_condition = Condition(self._state_lock)
        self._unique_waiting_blocking_threads = set()
        self._unique_waiting_count = 0
        self._unique_thread = None
        self._unique_count = 0
        self._shared_threads = {}

    def _wait(
        self,
        condition: Callable[[], bool],
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
    ) -> bool:
        """Wait until a condition is False.

        :param condition: The condition to check.
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

        if not condition():
            # We don't need to wait
            return True

        if not blocking:
            # Need to wait but told not to
            return False

        if timeout == -1:
            # wait with no timeout
            while condition():
                if task_manager.is_cancel_requested():
                    return False
                self._state_condition.wait()
            return True

        else:
            # Wait with a timeout
            end_time = time.time() + timeout
            while condition():
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
                and self._unique_waiting_blocking_threads.intersection(
                    self._shared_threads
                )
            ):
                # This thread has acquired the lock in shared mode
                # At least one other thread has acquired the lock in shared mode and is also waiting for unique mode.
                # If they both block indefinitely then neither will complete
                logging.warning("Probable deadlock")
            self._unique_waiting_count += 1
            if blocking and timeout == -1:
                # If it could block forever, add to this set
                self._unique_waiting_blocking_threads.add(ident)

            def on_cancel() -> None:
                self._state_condition.notify_all()

            task_manager.register_on_cancel(on_cancel)

            locked = self._wait(
                lambda: self._unique_thread not in (None, ident)
                or self._shared_threads.keys() not in (set(), {ident}),
                blocking,
                timeout,
                task_manager,
            )

            task_manager.unregister_on_cancel(on_cancel)

            self._unique_waiting_count -= 1
            self._unique_waiting_blocking_threads.discard(ident)
            if not locked:
                return False
            # Lock it
            self._unique_thread = ident
            self._unique_count += 1
            return True

    def release_unique(self) -> None:
        """
        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        Release the unique hold on the lock. This must be called by the same thread that acquired it.
        This must be called exactly the same number of times as :meth:`acquire_unique` was called.
        """
        with self._state_lock:
            if self._unique_thread != get_ident():
                raise RuntimeError("Lock released by a thread that does not own it.")

            self._unique_count -= 1
            if self._unique_count == 0:
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

            def condition() -> bool:
                locked_unique_other = bool(
                    # Is it locked in unique mode by another thread
                    self._unique_thread is not None
                    and self._unique_thread != ident
                )
                other_waiting_unique = bool(
                    # Has a thread requested unique access and this thread has not yet acquired in shared mode.
                    # Without this, new threads could join in shared mode thus indefinitely blocking unique calls
                    self._unique_waiting_count
                    and self._shared_threads
                    and ident not in self._shared_threads
                )
                return locked_unique_other or other_waiting_unique

            def on_cancel() -> None:
                self._state_condition.notify_all()

            task_manager.register_on_cancel(on_cancel)

            locked = self._wait(condition, blocking, timeout, task_manager)

            task_manager.unregister_on_cancel(on_cancel)

            if not locked:
                return False
            # Not unique locked or unique locked by the current thread
            self._shared_threads.setdefault(ident, 0)
            self._shared_threads[ident] += 1
            return True

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
