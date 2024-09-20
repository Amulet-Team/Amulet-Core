import abc
from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

from _typeshed import Incomplete

from .signal import Signal as Signal
from .signal import SignalInstance as SignalInstance

T = TypeVar("T")

class TaskCancelled(Exception):
    """Exception to be raised by the callee when a task is cancelled.

    The callee may define a custom return instead of using this.
    """

class AbstractCancelManager(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def cancel(self) -> None:
        """Request the operation be canceled.

        It is down to the operation to implement support for this.
        """

    @abstractmethod
    def is_cancel_requested(self) -> bool:
        """Has cancel been called to signal that the operation should be canceled."""

    @abstractmethod
    def register_on_cancel(self, callback: Callable[[], None]) -> None:
        """Register a function to get called when :meth:`cancel` is called."""

    @abstractmethod
    def unregister_on_cancel(self, callback: Callable[[], None]) -> None:
        """Unregister a registered function from being called when :meth:`cancel` is called."""

class VoidCancelManager(AbstractCancelManager):
    def cancel(self) -> None: ...
    def is_cancel_requested(self) -> bool: ...
    def register_on_cancel(self, callback: Callable[[], None]) -> None: ...
    def unregister_on_cancel(self, callback: Callable[[], None]) -> None: ...

class Pointer(Generic[T]):
    value: T
    def __init__(self, value: T) -> None: ...

class _CancelManager(AbstractCancelManager):
    def __init__(
        self, cancelled: Pointer[bool], cancel_signal: SignalInstance[()]
    ) -> None: ...
    def cancel(self) -> None: ...
    def is_cancel_requested(self) -> bool: ...
    def register_on_cancel(self, callback: Callable[[], None]) -> None: ...
    def unregister_on_cancel(self, callback: Callable[[], None]) -> None: ...

class CancelManager(_CancelManager):
    def __init__(self) -> None: ...

class AbstractProgressManager(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def update_progress(self, progress: float) -> None:
        """Notify the caller of the updated progress.

        :param progress: The new progress to relay to the caller. 0.0-1.0
        """

    @abstractmethod
    def update_progress_text(self, text: str) -> None:
        """Notify the caller of the updated progress.

        :param text: The new message to relay to the caller.
        """

    @abstractmethod
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> AbstractProgressManager:
        """Get a child ExecutionContext.

        If calling multiple functions, this allows segmenting the reported time.

        :param progress_min: The minimum progress for the child to use 0.0-1.0
        :param progress_max: The maximum progress for the child to use 0.0-1.0
        :return: A new ExecutionContext
        """

class VoidProgressManager(AbstractProgressManager):
    def update_progress(self, progress: float) -> None: ...
    def update_progress_text(self, text: str) -> None: ...
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> VoidProgressManager: ...

class _ProgressManager(AbstractProgressManager):
    def __init__(
        self,
        progress_change: SignalInstance[float],
        progress_text_change: SignalInstance[str],
        progress_min: float,
        progress_max: float,
    ) -> None: ...
    def update_progress(self, progress: float) -> None: ...
    def update_progress_text(self, text: str) -> None: ...
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> _ProgressManager: ...

class ProgressManager(_ProgressManager):
    progress_change: Incomplete
    progress_text_change: Incomplete
    def __init__(self) -> None: ...

class AbstractTaskManager(
    AbstractCancelManager, AbstractProgressManager, ABC, metaclass=abc.ABCMeta
): ...

class VoidTaskManager(VoidCancelManager, VoidProgressManager, AbstractTaskManager):
    """An empty Execution Context that ignores all calls."""

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

class TaskManager(_TaskManager):
    def __init__(self) -> None: ...
