from __future__ import annotations

import abc
import typing
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from amulet.utils.signal._signal import Signal, SignalInstance

__all__ = [
    "ABC",
    "AbstractCancelManager",
    "AbstractProgressManager",
    "AbstractTaskManager",
    "CancelManager",
    "Generic",
    "Pointer",
    "ProgressManager",
    "Signal",
    "SignalInstance",
    "T",
    "TaskCancelled",
    "TaskManager",
    "TypeVar",
    "VoidCancelManager",
    "VoidProgressManager",
    "VoidTaskManager",
    "abstractmethod",
]

class AbstractCancelManager(abc.ABC):
    def cancel(self) -> None:
        """
        Request the operation be canceled.

                It is down to the operation to implement support for this.

        """

    def is_cancel_requested(self) -> bool:
        """
        Has cancel been called to signal that the operation should be canceled.
        """

    def register_on_cancel(self, callback: typing.Callable[[], None]) -> None:
        """
        Register a function to get called when :meth:`cancel` is called.
        """

    def unregister_on_cancel(self, callback: typing.Callable[[], None]) -> None:
        """
        Unregister a registered function from being called when :meth:`cancel` is called.
        """

class AbstractProgressManager(abc.ABC):
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> AbstractProgressManager:
        """
        Get a child ExecutionContext.

                If calling multiple functions, this allows segmenting the reported time.

                :param progress_min: The minimum progress for the child to use 0.0-1.0
                :param progress_max: The maximum progress for the child to use 0.0-1.0
                :return: A new ExecutionContext

        """

    def update_progress(self, progress: float) -> None:
        """
        Notify the caller of the updated progress.

                :param progress: The new progress to relay to the caller. 0.0-1.0

        """

    def update_progress_text(self, text: str) -> None:
        """
        Notify the caller of the updated progress.

                :param text: The new message to relay to the caller.

        """

class AbstractTaskManager(AbstractCancelManager, AbstractProgressManager, abc.ABC):
    pass

class CancelManager(_CancelManager):
    @staticmethod
    def _cancel_signal(*args, **kwargs): ...
    def __init__(self) -> None: ...

class Pointer(typing.Generic):
    def __init__(self, value: T) -> None: ...

class ProgressManager(_ProgressManager):
    @staticmethod
    def progress_change(*args, **kwargs): ...
    @staticmethod
    def progress_text_change(*args, **kwargs): ...
    def __init__(self) -> None: ...

class TaskCancelled(Exception):
    """
    Exception to be raised by the callee when a task is cancelled.

        The callee may define a custom return instead of using this.

    """

class TaskManager(_TaskManager):
    def __init__(self) -> None: ...

class VoidCancelManager(AbstractCancelManager):
    def cancel(self) -> None: ...
    def is_cancel_requested(self) -> bool: ...
    def register_on_cancel(self, callback: typing.Callable[[], None]) -> None: ...
    def unregister_on_cancel(self, callback: typing.Callable[[], None]) -> None: ...

class VoidProgressManager(AbstractProgressManager):
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> VoidProgressManager: ...
    def update_progress(self, progress: float) -> None: ...
    def update_progress_text(self, text: str) -> None: ...

class VoidTaskManager(VoidCancelManager, VoidProgressManager, AbstractTaskManager):
    """
    An empty Execution Context that ignores all calls.
    """

class _CancelManager(AbstractCancelManager):
    def __init__(
        self, cancelled: Pointer[bool], cancel_signal: SignalInstance[()]
    ) -> None: ...
    def cancel(self) -> None: ...
    def is_cancel_requested(self) -> bool: ...
    def register_on_cancel(self, callback: typing.Callable[[], None]) -> None: ...
    def unregister_on_cancel(self, callback: typing.Callable[[], None]) -> None: ...

class _ProgressManager(AbstractProgressManager):
    def __init__(
        self,
        progress_change: SignalInstance[float],
        progress_text_change: SignalInstance[str],
        progress_min: float,
        progress_max: float,
    ) -> None: ...
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> _ProgressManager: ...
    def update_progress(self, progress: float) -> None: ...
    def update_progress_text(self, text: str) -> None: ...

class _TaskManager(CancelManager, ProgressManager, AbstractTaskManager):
    def __init__(
        self,
        cancelled: Pointer[bool],
        cancel_signal: SignalInstance[()],
        progress_change: SignalInstance[float],
        progress_text_change: SignalInstance[str],
        progress_min: float,
        progress_max: float,
    ) -> None: ...
    def get_child(self, progress_min: float, progress_max: float) -> _TaskManager: ...

T: typing.TypeVar  # value = ~T
