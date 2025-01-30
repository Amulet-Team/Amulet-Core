from __future__ import annotations

import contextlib
import typing

import amulet.utils.mutex
import amulet.utils.task_manager.cancel_manager

__all__ = [
    "Lock",
    "LockNotAcquired",
    "OrderedSharedLock",
    "RLock",
    "SharedLock",
    "SharedLockContextManager",
    "UniqueLockContextManager",
]

class Lock:
    """
    A wrapper for std::mutex.
    """

    def __enter__(self) -> None: ...
    def __exit__(
        self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any
    ) -> None: ...
    def __init__(self) -> None: ...
    def acquire(self, blocking: bool = True) -> bool: ...
    def release(self) -> None: ...

class LockNotAcquired(RuntimeError):
    """
    An exception raised if the lock was not acquired.
    """

class OrderedSharedLock:
    """
    This is a custom lock implementation that can be acquired in
    1) unique mode.
        - This is the normal mode where only this thread can use the resource.
        - All other acquires block until it is released.
    2) shared mode.
        - This allows multiple threads to acquire the resource at the same time.
        - This is useful if multiple threads want to read a resource but not write to it.
        - If the resource is locked in unique mode this will block.
        - Once locked in shared mode it will block unique acquires until all shared threads release it.
    Tasks are prioritised in the order the call is made
    """

    @typing.overload
    def __init__(self, mutex: amulet.utils.mutex.OrderedSharedTimedMutex) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def acquire_shared(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
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

    def acquire_unique(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool:
        """
        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        Acquire the lock in unique mode. This is equivalent to threading.Lock.acquire
        With improper use this can lead to a deadlock.
        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: True if the lock was acquired otherwise False.
        """

    def release_shared(self) -> None:
        """
        Only use this if you know what you are doing. Consider using :meth:`shared` instead
        Release the shared hold on the lock. This must be called by the same thread that acquired it.
        This must be called exactly the same number of times as :meth:`acquire_shared` was called.
        """

    def release_unique(self) -> None:
        """
        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        Release the unique hold on the lock. This must be called by the same thread that acquired it.
        This must be called exactly the same number of times as :meth:`acquire_unique` was called.
        """

    def shared(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> SharedLockContextManager:
        """
        Acquire the lock in shared mode.
        This is used as follows

        >>> lock: OrderedSharedLock
        >>> with lock.shared():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        If the lock is acquired by a different thread in unique mode then this will block until it is finished.
        If the lock is acquired in unique mode by this thread or by other threads in shared mode then this will acquire
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

    def unique(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> UniqueLockContextManager:
        """
        Acquire the lock in unique mode.
        This is used as follows

        >>> lock: OrderedSharedLock
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

class RLock:
    """
    A wrapper for std::recursive_mutex.
    """

    def __enter__(self) -> None: ...
    def __exit__(
        self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any
    ) -> None: ...
    def __init__(self) -> None: ...
    def acquire(self, blocking: bool = True) -> bool: ...
    def release(self) -> None: ...

class SharedLock:
    """
    A wrapper for std::shared_mutex.
    """

    def __init__(self) -> None: ...
    def acquire_shared(self, blocking: bool = True) -> bool: ...
    def acquire_unique(self, blocking: bool = True) -> bool: ...
    def release_shared(self) -> None: ...
    def release_unique(self) -> None: ...
    def shared(self) -> contextlib.AbstractContextManager[None, bool | None]: ...
    def unique(self) -> contextlib.AbstractContextManager[None, bool | None]: ...

class SharedLockContextManager:
    def __enter__(self) -> None: ...
    def __exit__(
        self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any
    ) -> None: ...

class UniqueLockContextManager:
    def __enter__(self) -> None: ...
    def __exit__(
        self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any
    ) -> None: ...
