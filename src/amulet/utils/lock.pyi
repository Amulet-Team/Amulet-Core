from __future__ import annotations

import contextlib
import typing

import amulet.utils.task_manager.cancel_manager

__all__ = [
    "Deadlock",
    "Lock",
    "LockNotAcquired",
    "OrderedLock",
    "RLock",
    "SharedLock",
    "ThreadAccessMode",
    "ThreadShareMode",
]

class Deadlock(RuntimeError):
    """
    An exception raised in some deadlock cases.
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
    This is a custom mutex implementation that prioritises acquisition order and allows parallelism where possible.
    The acquirer can define the required permissions for this thread and permissions for other parallel threads.
    It also supports cancelling waiting through a CancelManager instance.
    """

    def __call__(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
        thread_mode: tuple[ThreadAccessMode, ThreadShareMode] = ...,
    ) -> contextlib.AbstractContextManager[None, bool | None]:
        """
        A context manager to acquire and release the lock.
        Thread safe.

        >>> lock: OrderedLock
        >>> with lock():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        Entering the context manager acquires the lock.
        If the lock could not be acquired :class:`LockNotAcquired` is raised.
        Exiting the context manager releases the lock.

        :param blocking:
            If true (default) entering the context manager will block until the lock is acquired, the timeout is reached or the task is cancelled.
            If false entering the context manager will immediately fail if the lock could not be acquired.
        :param timeout:
            The maximum number of seconds to block for when entering the context manager.
            Has no effect if blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :param thread_mode: The permissions for the current and other parallel threads.
        :return: contextlib.AbstractContextManager[None]
        """

    def __init__(self) -> None: ...
    def acquire(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
        thread_mode: tuple[ThreadAccessMode, ThreadShareMode] = ...,
    ) -> bool:
        """
        Acquire the lock.
        Thread safe.

        With improper use this can lead to a deadlock.
        Only use this if you know what you are doing. Consider using the context manager instead

        :param blocking:
            If true (default) this will block until the lock is acquired, the timeout is reached or the task is cancelled.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: The maximum number of seconds to block for. Has no effect if blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :param thread_mode: The permissions for the current and other parallel threads.
        :return: True if the lock was acquired otherwise False.
        """

    def release(self) -> None:
        """
        Release the lock.
        Must be called by the thread that locked it.
        Thread safe.

        Only use this if you know what you are doing. Consider using the context manager instead
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

class ThreadAccessMode:
    """
    Members:

      Read : This thread can only read.

      ReadWrite : This thread can read and write.
    """

    Read: typing.ClassVar[
        ThreadAccessMode
    ]  # value = amulet.utils.lock.ThreadAccessMode.Read
    ReadWrite: typing.ClassVar[
        ThreadAccessMode
    ]  # value = amulet.utils.lock.ThreadAccessMode.ReadWrite
    __members__: typing.ClassVar[
        dict[str, ThreadAccessMode]
    ]  # value = {'Read': amulet.utils.lock.ThreadAccessMode.Read, 'ReadWrite': amulet.utils.lock.ThreadAccessMode.ReadWrite}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class ThreadShareMode:
    """
    Members:

      Unique : Other threads can't run in parallel.

      SharedReadOnly : Other threads can only read in parallel.

      SharedReadWrite : Other threads can read and write in parallel.
    """

    SharedReadOnly: typing.ClassVar[
        ThreadShareMode
    ]  # value = amulet.utils.lock.ThreadShareMode.SharedReadOnly
    SharedReadWrite: typing.ClassVar[
        ThreadShareMode
    ]  # value = amulet.utils.lock.ThreadShareMode.SharedReadWrite
    Unique: typing.ClassVar[
        ThreadShareMode
    ]  # value = amulet.utils.lock.ThreadShareMode.Unique
    __members__: typing.ClassVar[
        dict[str, ThreadShareMode]
    ]  # value = {'Unique': amulet.utils.lock.ThreadShareMode.Unique, 'SharedReadOnly': amulet.utils.lock.ThreadShareMode.SharedReadOnly, 'SharedReadWrite': amulet.utils.lock.ThreadShareMode.SharedReadWrite}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...
