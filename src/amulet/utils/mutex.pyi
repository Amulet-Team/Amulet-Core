from __future__ import annotations

import datetime

import amulet.utils.task_manager.cancel_manager

__all__ = ["Deadlock", "OrderedSharedMutex", "OrderedSharedTimedMutex"]

class Deadlock(RuntimeError):
    pass

class OrderedSharedMutex:
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def lock(
        self,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> None: ...
    def lock_shared(
        self,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> None: ...
    def try_lock(self) -> bool: ...
    def try_lock_shared(self) -> bool: ...
    def unlock(self) -> None: ...
    def unlock_shared(self) -> None: ...

class OrderedSharedTimedMutex(OrderedSharedMutex):
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def try_lock_for(
        self,
        timeout_duration: datetime.timedelta,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool: ...
    def try_lock_shared_for(
        self,
        timeout_duration: datetime.timedelta,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool: ...
    def try_lock_shared_until(
        self,
        timeout_time: datetime.datetime,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool: ...
    def try_lock_until(
        self,
        timeout_time: datetime.datetime,
        cancel_manager: amulet.utils.task_manager.cancel_manager.AbstractCancelManager = ...,
    ) -> bool: ...
