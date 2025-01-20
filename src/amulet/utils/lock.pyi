from __future__ import annotations

import typing

import amulet.utils.mutex
import amulet.utils.task_manager.cancel_manager

__all__ = [
    "LockNotAcquired",
    "OrderedSharedLock",
    "SharedLockContextManager",
    "UniqueLockContextManager",
]

class LockNotAcquired(RuntimeError):
    """
    An exception raised if the lock was not acquired.
    """

class OrderedSharedLock:
    def __init__(self, arg0: amulet.utils.mutex.OrderedSharedTimedMutex) -> None: ...
    def acquire_shared(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool: ...
    def acquire_unique(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool: ...
    def release_shared(self) -> None: ...
    def release_unique(self) -> None: ...
    def shared(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> SharedLockContextManager: ...
    def unique(
        self,
        blocking: bool = True,
        timeout: float = -1.0,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> UniqueLockContextManager: ...

class SharedLockContextManager:
    def __enter__(self) -> None: ...
    def __exit__(
        self, arg0: typing.Any, arg1: typing.Any, arg2: typing.Any
    ) -> None: ...

class UniqueLockContextManager:
    def __enter__(self) -> None: ...
    def __exit__(
        self, arg0: typing.Any, arg1: typing.Any, arg2: typing.Any
    ) -> None: ...
