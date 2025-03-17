from __future__ import annotations

import typing

import amulet.utils.signal

__all__ = [
    "AbstractCancelManager",
    "CancelManager",
    "TaskCancelled",
    "VoidCancelManager",
]

class AbstractCancelManager:
    def cancel(self) -> None:
        """
        Request the operation be cancelled.
        It is down to the operation to implement support for this.
        Thread safe.
        """

    def is_cancel_requested(self) -> bool:
        """
        Has :meth:`cancel` been called to signal that the operation should be cancelled.
        Thread safe.
        """

    def register_cancel_callback(
        self, callback: typing.Callable[[], None]
    ) -> amulet.utils.signal.SignalToken[()]:
        """
        Register a function to get called when cancel is called.
        The callback will be called from the thread `cancel` is called in.
        Thread safe.
        """

    def unregister_cancel_callback(
        self, token: amulet.utils.signal.SignalToken[()]
    ) -> None:
        """
        Unregister a registered function from being called when cancel is called.
        Thread safe.
        """

class CancelManager(AbstractCancelManager):
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...

class TaskCancelled(Exception):
    pass

class VoidCancelManager(AbstractCancelManager):
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
