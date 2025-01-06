from __future__ import annotations

import typing

__all__ = [
    "AbstractCancelManager",
    "CancelManager",
    "TaskCancelled",
    "VoidCancelManager",
]

class AbstractCancelManager:
    def cancel(self) -> None: ...
    def is_cancel_requested(self) -> bool: ...
    def register_cancel_callback(self, callback: typing.Callable[[], None]) -> None: ...
    def unregister_cancel_callback(
        self, callback: typing.Callable[[], None]
    ) -> None: ...

class CancelManager(AbstractCancelManager):
    def __init__(self) -> None: ...

class TaskCancelled(Exception):
    pass

class VoidCancelManager(AbstractCancelManager):
    def __init__(self) -> None: ...

class _CancelManager(AbstractCancelManager):
    pass
