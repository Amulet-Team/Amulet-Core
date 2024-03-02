from __future__ import annotations

from typing import Generic, TypeVar, Self, Callable
from abc import ABC, abstractmethod

from .signal import Signal, SignalInstance


T = TypeVar("T")


class TaskManager(ABC):
    @abstractmethod
    def cancel(self) -> None:
        """Request the operation be canceled.

        It is down to the operation to implement support for this.
        """
        raise NotImplementedError

    @abstractmethod
    def is_cancel_requested(self) -> bool:
        """Has cancel been called to signal that the operation should be canceled."""
        raise NotImplementedError

    @abstractmethod
    def register_on_cancel(self, callback: Callable[[], None]) -> None:
        """Register a function to get called when :meth:`cancel` is called."""
        raise NotImplementedError

    @abstractmethod
    def unregister_on_cancel(self, callback: Callable[[], None]) -> None:
        """Unregister a registered function from being called when :meth:`cancel` is called."""
        raise NotImplementedError

    @abstractmethod
    def update_progress(self, progress: float) -> None:
        """Notify the caller of the updated progress.

        :param progress: The new progress to relay to the caller. 0.0-1.0
        """
        raise NotImplementedError

    @abstractmethod
    def update_progress_text(self, text: str) -> None:
        """Notify the caller of the updated progress.

        :param text: The new message to relay to the caller.
        """
        raise NotImplementedError

    @abstractmethod
    def get_child(self, progress_min: float, progress_max: float) -> TaskManager:
        """Get a child ExecutionContext.

        If calling multiple functions, this allows segmenting the reported time.

        :param progress_min: The minimum progress for the child to use 0.0-1.0
        :param progress_max: The maximum progress for the child to use 0.0-1.0
        :return: A new ExecutionContext
        """
        raise NotImplementedError


class Pointer(Generic[T]):
    value: T

    def __init__(self, value: T) -> None:
        self.value = value


class _RelayChainTaskManager(TaskManager):
    def __init__(
        self,
        cancelled: Pointer[bool],
        cancel_signal: SignalInstance[()],
        progress_change: SignalInstance[float],
        progress_text_change: SignalInstance[str],
        progress_min: float,
        progress_max: float,
    ) -> None:
        self._cancelled = cancelled
        self._on_cancel = cancel_signal
        self._progress_change = progress_change
        self._progress_text_change = progress_text_change
        assert 0.0 <= progress_min <= progress_max <= 1.0
        self._progress_min = progress_min
        self._progress_delta = progress_max - progress_min

    def cancel(self) -> None:
        self._cancelled.value = True
        self._on_cancel.emit()

    def is_cancel_requested(self) -> bool:
        return self._cancelled.value

    def register_on_cancel(self, callback: Callable[[], None]) -> None:
        self._on_cancel.connect(callback)

    def unregister_on_cancel(self, callback: Callable[[], None]) -> None:
        self._on_cancel.disconnect(callback)

    def update_progress(self, progress: float) -> None:
        assert 0.0 <= progress <= 1.0
        self._progress_change.emit(self._progress_min + progress * self._progress_delta)

    def update_progress_text(self, text: str) -> None:
        self._progress_text_change.emit(text)

    def get_child(
        self, progress_min: float, progress_max: float
    ) -> _RelayChainTaskManager:
        assert 0.0 <= progress_min <= progress_max <= 1.0
        return _RelayChainTaskManager(
            self._cancelled,
            self._on_cancel,
            self._progress_change,
            self._progress_text_change,
            self._progress_min + progress_min * self._progress_delta,
            self._progress_min + progress_max * self._progress_delta,
        )


class RelayTaskManager(_RelayChainTaskManager):
    progress_change = Signal[float](float)
    progress_text_change = Signal[str](str)
    _cancel_signal = Signal[()]()

    def __init__(self) -> None:
        super().__init__(
            Pointer[bool](False),
            self._cancel_signal,
            self.progress_change,
            self.progress_text_change,
            0.0,
            1.0,
        )


class VoidTaskManager(TaskManager):
    """An empty Execution Context that ignores all calls."""

    def cancel(self) -> None:
        pass

    def is_cancel_requested(self) -> bool:
        return False

    def register_on_cancel(self, callback: Callable[[], None]) -> None:
        pass

    def unregister_on_cancel(self, callback: Callable[[], None]) -> None:
        pass

    def update_progress(self, progress: float) -> None:
        pass

    def update_progress_text(self, text: str) -> None:
        pass

    def get_child(self, progress_min: float, progress_max: float) -> Self:
        return self
