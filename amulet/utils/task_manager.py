from __future__ import annotations

from typing import Generic, TypeVar, Callable
from abc import ABC, abstractmethod

from .signal import Signal, SignalInstance


T = TypeVar("T")


class TaskCancelled(Exception):
    """Exception to be raised by the callee when a task is cancelled.

    The callee may define a custom return instead of using this.
    """


class AbstractCancelManager(ABC):
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


class VoidCancelManager(AbstractCancelManager):
    def cancel(self) -> None:
        pass

    def is_cancel_requested(self) -> bool:
        return False

    def register_on_cancel(self, callback: Callable[[], None]) -> None:
        pass

    def unregister_on_cancel(self, callback: Callable[[], None]) -> None:
        pass


class Pointer(Generic[T]):
    value: T

    def __init__(self, value: T) -> None:
        self.value = value


class _CancelManager(AbstractCancelManager):
    def __init__(
        self,
        cancelled: Pointer[bool],
        cancel_signal: SignalInstance[()],
    ) -> None:
        self._cancelled = cancelled
        self._on_cancel = cancel_signal

    def cancel(self) -> None:
        self._cancelled.value = True
        self._on_cancel.emit()

    def is_cancel_requested(self) -> bool:
        return self._cancelled.value

    def register_on_cancel(self, callback: Callable[[], None]) -> None:
        self._on_cancel.connect(callback)

    def unregister_on_cancel(self, callback: Callable[[], None]) -> None:
        self._on_cancel.disconnect(callback)


class CancelManager(_CancelManager):
    _cancel_signal = Signal[()]()

    def __init__(self) -> None:
        super().__init__(
            Pointer[bool](False),
            self._cancel_signal,
        )


class AbstractProgressManager(ABC):
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
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> AbstractProgressManager:
        """Get a child ExecutionContext.

        If calling multiple functions, this allows segmenting the reported time.

        :param progress_min: The minimum progress for the child to use 0.0-1.0
        :param progress_max: The maximum progress for the child to use 0.0-1.0
        :return: A new ExecutionContext
        """
        raise NotImplementedError


class VoidProgressManager(AbstractProgressManager):
    def update_progress(self, progress: float) -> None:
        pass

    def update_progress_text(self, text: str) -> None:
        pass

    def get_child(
        self, progress_min: float, progress_max: float
    ) -> VoidProgressManager:
        return self


class _ProgressManager(AbstractProgressManager):
    def __init__(
        self,
        progress_change: SignalInstance[float],
        progress_text_change: SignalInstance[str],
        progress_min: float,
        progress_max: float,
    ) -> None:
        self._progress_change = progress_change
        self._progress_text_change = progress_text_change
        assert 0.0 <= progress_min <= progress_max <= 1.0
        self._progress_min = progress_min
        self._progress_delta = progress_max - progress_min

    def update_progress(self, progress: float) -> None:
        assert 0.0 <= progress <= 1.0
        self._progress_change.emit(self._progress_min + progress * self._progress_delta)

    def update_progress_text(self, text: str) -> None:
        self._progress_text_change.emit(text)

    def get_child(self, progress_min: float, progress_max: float) -> _ProgressManager:
        assert 0.0 <= progress_min <= progress_max <= 1.0
        return _ProgressManager(
            self._progress_change,
            self._progress_text_change,
            self._progress_min + progress_min * self._progress_delta,
            self._progress_min + progress_max * self._progress_delta,
        )


class ProgressManager(_ProgressManager):
    progress_change = Signal[float](float)
    progress_text_change = Signal[str](str)

    def __init__(self) -> None:
        super().__init__(
            self.progress_change,
            self.progress_text_change,
            0.0,
            1.0,
        )


class AbstractTaskManager(AbstractCancelManager, AbstractProgressManager, ABC):
    pass


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
    ) -> None:
        _CancelManager.__init__(self, cancelled, cancel_signal)
        _ProgressManager.__init__(
            self,
            progress_change,
            progress_text_change,
            progress_min,
            progress_max,
        )

    def get_child(self, progress_min: float, progress_max: float) -> _TaskManager:
        assert 0.0 <= progress_min <= progress_max <= 1.0
        return _TaskManager(
            self._cancelled,
            self._on_cancel,
            self._progress_change,
            self._progress_text_change,
            self._progress_min + progress_min * self._progress_delta,
            self._progress_min + progress_max * self._progress_delta,
        )


class TaskManager(_TaskManager):
    def __init__(self) -> None:
        super().__init__(
            Pointer[bool](False),
            self._cancel_signal,
            self.progress_change,
            self.progress_text_change,
            0.0,
            1.0,
        )
