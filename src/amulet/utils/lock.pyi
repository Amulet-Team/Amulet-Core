from __future__ import annotations

import contextlib
import typing

import amulet.utils.task_manager.cancel_manager

__all__ = ["Deadlock", "Lock", "LockNotAcquired", "OrderedLock", "RLock", "SharedLock"]

class Deadlock(RuntimeError):
    """
    This exception signals that a deadlock occurred when locking a lock.
    Not all deadlock cases raise an exception.
    """

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

class OrderedLock:
    """
    This is a custom lock implementation that can be acquired in:
    1) Unique mode.
        - Only one thread can use the resource.
        - Blocks until no thread holds the lock
        - Stops all other threads acquiring the lock until released.
    2) Shared read-only mode.
        - Multiple threads can read (but not write) the resource at the same time.
        - Can be acquired in parallel with read mode.
        - Blocks until no thread holds the lock in unique or write mode.
        - Stops other threads acquiring in unique and write mode until released.
    3) Shared read mode.
        - This thread may only read but other threads may write in parallel.
        - Only thread-safe functions may be called in this mode.
        - Can be acquired in parallel with read-only mode or write mode (not at the same time)
        - Blocks until no thread holds the lock in unique mode.
        - Stops other threads acquiring in unique mode until released.
    4) Shared read-write mode.
        - This thread may read and write in parallel with other reading and writing threads.
        - Only thread-safe functions may be called in this mode.
        - Can be acquired in parallel with read mode.
        - Blocks until no thread holds the lock in unique or read-only mode.
        - Stops other threads acquiring in unique and read-only mode until released.
    The lock is ordered meaning it prioritises older acquires over newer ones.
    It also supports cancelling waiting through a CancelManager instance.
    """

    def __init__(self) -> None: ...
    def acquire_shared_read(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool:
        """
        Acquires the lock in shared read mode.
        Blocks until no thread holds the lock in unique mode.
        Stops other threads acquiring in unique mode until released.

        With improper use this can lead to a deadlock.
        Only use this if you know what you are doing. Consider using :meth:`shared_read` instead

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: True if the lock was acquired otherwise False.
        """

    def acquire_shared_read_only(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool:
        """
        Acquires the lock in shared read-only mode.
        Blocks until no thread holds the lock in unique or write mode.
        Stops other threads acquiring in unique and write mode until released.

        With improper use this can lead to a deadlock.
        Only use this if you know what you are doing. Consider using :meth:`shared_read_only` instead

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: True if the lock was acquired otherwise False.
        """

    def acquire_shared_read_write(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool:
        """
        Acquires the lock in shared read-write mode.
        Blocks until no thread holds the lock in unique or read-only mode.
        Stops other threads acquiring in unique and read-only mode until released.

        With improper use this can lead to a deadlock.
        Only use this if you know what you are doing. Consider using :meth:`shared_read_write` instead

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
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
        Acquire the lock in unique mode.
        Blocks until no thread holds the lock.
        Stops all other threads acquiring the lock until released.

        With improper use this can lead to a deadlock.
        Only use this if you know what you are doing. Consider using :meth:`unique` instead

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: True if the lock was acquired otherwise False.
        """

    def release_shared(self) -> None:
        """
        Release the lock from any shared mode.
        Must be called by the thread that locked it.

        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        """

    def release_unique(self) -> None:
        """
        Release the lock from unique mode.
        Must be called by the thread that locked it.

        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        """

    def shared_read(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> contextlib.AbstractContextManager[None, bool | None]:
        """
        A context manager to acquire and release the lock in shared read mode.

        >>> lock: OrderedLock
        >>> with lock.shared():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        Blocks until no thread holds the lock in unique mode when entering the context manager.
        Once acquired stops other threads acquiring in unique mode until released.
        Exiting the context manager releases the lock.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: contextlib.AbstractContextManager[None]
        :raises: LockNotAcquired if the lock could not be acquired.
        """

    def shared_read_only(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> contextlib.AbstractContextManager[None, bool | None]:
        """
        A context manager to acquire and release the lock in shared read-only mode.

        >>> lock: OrderedLock
        >>> with lock.shared_read_only():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        Blocks until no thread holds the lock in unique or write mode when entering the context manager.
        Once acquired stops other threads acquiring in unique and write mode until released.
        Exiting the context manager releases the lock.

        If another thread wants to acquire the lock in unique mode it will block until all threads have finished in
        shared mode.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: contextlib.AbstractContextManager[None]
        :raises: LockNotAcquired if the lock could not be acquired.
        """

    def shared_read_write(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> contextlib.AbstractContextManager[None, bool | None]:
        """
        A context manager to acquire and release the lock in shared read-write mode.

        >>> lock: OrderedLock
        >>> with lock.shared():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        Blocks until no thread holds the lock in unique or read-only mode when entering the context manager.
        Once acquired stops other threads acquiring in unique and read-only mode until released.
        Exiting the context manager releases the lock.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: contextlib.AbstractContextManager[None]
        :raises: LockNotAcquired if the lock could not be acquired.
        """

    def unique(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> contextlib.AbstractContextManager[None, bool | None]:
        """
        A context manager to acquire and release the lock in unique mode.

        >>> lock: OrderedLock
        >>> with lock.unique():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        Blocks until no thread holds the lock when entering the context manager.
        Once acquired stops all other threads acquiring the lock until released.
        Exiting the context manager releases the lock.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :return: contextlib.AbstractContextManager[None]
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
