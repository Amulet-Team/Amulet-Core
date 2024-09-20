from typing import Iterator

from _typeshed import Incomplete

from .task_manager import AbstractCancelManager as AbstractCancelManager
from .task_manager import TaskCancelled as TaskCancelled
from .task_manager import VoidCancelManager as VoidCancelManager

log: Incomplete

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

    def __init__(self) -> None: ...
    def acquire_unique(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...,
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

    def release_unique(self) -> None:
        """
        Only use this if you know what you are doing. Consider using :meth:`unique` instead
        Release the unique hold on the lock. This must be called by the same thread that acquired it.
        This must be called exactly the same number of times as :meth:`acquire_unique` was called.
        """

    def acquire_shared(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...,
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

    def release_shared(self) -> None:
        """
        Only use this if you know what you are doing. Consider using :meth:`shared` instead
        Release the shared hold on the lock. This must be called by the same thread that acquired it.
        This must be called exactly the same number of times as :meth:`acquire_shared` was called.
        """

    def unique(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...,
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

    def shared(
        self,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...,
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
