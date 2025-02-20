from __future__ import annotations

import contextlib
import typing

import amulet.utils.task_manager.cancel_manager

__all__ = [
    "CurrentThreadMode",
    "Deadlock",
    "Lock",
    "LockNotAcquired",
    "OrderedLock",
    "OtherThreadMode",
    "RLock",
    "SharedLock",
]

class CurrentThreadMode:
    """
    Members:

      Read : This thread can only read.

      ReadWrite : This thread can read and write.
    """

    Read: typing.ClassVar[
        CurrentThreadMode
    ]  # value = amulet.utils.lock.CurrentThreadMode.Read
    ReadWrite: typing.ClassVar[
        CurrentThreadMode
    ]  # value = amulet.utils.lock.CurrentThreadMode.ReadWrite
    __members__: typing.ClassVar[
        dict[str, CurrentThreadMode]
    ]  # value = {'Read': amulet.utils.lock.CurrentThreadMode.Read, 'ReadWrite': amulet.utils.lock.CurrentThreadMode.ReadWrite}
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
    This is a custom mutex implementation that prioritises acquisition order and allows parallelism where possible.
    The acquirer can define the required permissions for this thread and permissions for other parallel threads.
    It also supports cancelling waiting through a CancelManager instance.
    """

    def __call__(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
        self_thread_mode: CurrentThreadMode = ...,
        other_thread_mode: OtherThreadMode = ...,
    ) -> contextlib.AbstractContextManager[None, bool | None]:
        """
        A context manager to acquire and release the lock.

        >>> lock: OrderedLock
        >>> with lock():
        >>>     # code with lock acquired
        >>> # the lock will automatically be released here

        Blocks until no thread holds the lock when entering the context manager.
        Once acquired, stops all other threads acquiring the lock until released.
        Exiting the context manager releases the lock.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :param self_thread_mode: The permissions the current thread requires.
        :param other_thread_mode: The permissions other threads can use in parallel.
        :return: contextlib.AbstractContextManager[None]
        :raises: LockNotAcquired if the lock could not be acquired.
        """

    def __init__(self) -> None: ...
    def acquire(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
        self_thread_mode: CurrentThreadMode = ...,
        other_thread_mode: OtherThreadMode = ...,
    ) -> bool:
        """
        Acquire the lock.
        Stops all other threads acquiring the lock until released.

        With improper use this can lead to a deadlock.
        Only use this if you know what you are doing. Consider using the context manager instead

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: A custom object through which acquiring can be cancelled.
            This effectively manually triggers timeout.
            This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
        :param self_thread_mode: The permissions the current thread requires.
        :param other_thread_mode: The permissions other threads can use in parallel.
        :return: True if the lock was acquired otherwise False.
        """

    def release(self) -> None:
        """
        Release the lock.
        Must be called by the thread that locked it.

        Only use this if you know what you are doing. Consider using the context manager instead
        """

class OtherThreadMode:
    """
    Members:

      Null : Other threads can't do anything.

      Read : Other threads can only read.

      ReadWrite : Other threads can read and write.
    """

    Null: typing.ClassVar[
        OtherThreadMode
    ]  # value = amulet.utils.lock.OtherThreadMode.Null
    Read: typing.ClassVar[
        OtherThreadMode
    ]  # value = amulet.utils.lock.OtherThreadMode.Read
    ReadWrite: typing.ClassVar[
        OtherThreadMode
    ]  # value = amulet.utils.lock.OtherThreadMode.ReadWrite
    __members__: typing.ClassVar[
        dict[str, OtherThreadMode]
    ]  # value = {'Null': amulet.utils.lock.OtherThreadMode.Null, 'Read': amulet.utils.lock.OtherThreadMode.Read, 'ReadWrite': amulet.utils.lock.OtherThreadMode.ReadWrite}
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
