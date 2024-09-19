from __future__ import annotations

import logging as logging
import time as time
from _thread import allocate_lock as Lock
from _thread import get_ident
from contextlib import contextmanager
from threading import Condition

import amulet.utils.task_manager
from amulet.utils.task_manager import (
    AbstractCancelManager,
    TaskCancelled,
    VoidCancelManager,
)

__all__ = [
    "AbstractCancelManager",
    "Condition",
    "Lock",
    "LockNotAcquired",
    "ShareableRLock",
    "TaskCancelled",
    "VoidCancelManager",
    "contextmanager",
    "get_ident",
    "log",
    "logging",
    "time",
]

class LockNotAcquired(amulet.utils.task_manager.TaskCancelled):
    """
    An exception raised if the lock was not acquired.
    """

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

    @staticmethod
    def shared(*args, **kwds) -> typing.Iterator[NoneType]:
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

    @staticmethod
    def unique(*args, **kwds) -> typing.Iterator[NoneType]:
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

    def __init__(self) -> None: ...
    def _wait(
        self,
        exit_condition: typing.Callable[[], bool],
        blocking: bool = True,
        timeout: float = -1,
        task_manager: amulet.utils.task_manager.AbstractCancelManager = ...,
    ) -> bool:
        """
        Wait until a condition is False.

                :param exit_condition: The condition to check.
                :param blocking: Should this block until the lock can be acquired. Default is True.
                    If false and the lock cannot be acquired on the first try, this returns False.
                :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
                :param task_manager: A custom object through which acquiring can be cancelled.
                    This effectively manually triggers timeout.
                    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.
                :return: True if the lock was acquired, otherwise False.

        """

    def acquire_shared(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: amulet.utils.task_manager.AbstractCancelManager = ...,
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
        timeout: float = -1,
        task_manager: amulet.utils.task_manager.AbstractCancelManager = ...,
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

log: logging.Logger  # value = <Logger amulet.utils.shareable_lock (INFO)>
