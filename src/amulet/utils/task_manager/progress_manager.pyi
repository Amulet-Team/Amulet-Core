from __future__ import annotations

import typing

import amulet.utils.signal

__all__ = ["AbstractProgressManager", "ProgressManager", "VoidProgressManager"]

class AbstractProgressManager:
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> AbstractProgressManager:
        """
        Get a child ProgressManager.
        If calling multiple functions, this allows segmenting the reported time.
        Thread safe.
        """

    def register_progress_callback(
        self, callback: typing.Callable[[float], None]
    ) -> amulet.utils.signal.SignalToken[float]:
        """
        Register a function to get called when progress changes.
        The callback will be called from the thread `update_progress` is called in.
        Thread safe.
        """

    def register_progress_text_callback(
        self, callback: typing.Callable[[str], None]
    ) -> amulet.utils.signal.SignalToken[str]:
        """
        Register a function to get called when progress changes.
        The callback will be called from the thread `update_progress` is called in.
        Thread safe.
        """

    def unregister_progress_callback(
        self, token: amulet.utils.signal.SignalToken[float]
    ) -> None:
        """
        Unregister a registered function from being called when update_progress is called.
        Thread safe.
        """

    def unregister_progress_text_callback(
        self, token: amulet.utils.signal.SignalToken[str]
    ) -> None:
        """
        Unregister a registered function from being called when update_progress is called.
        Thread safe.
        """

    def update_progress(self, progress: float) -> None:
        """
        Notify the caller of the updated progress.
        progress must be in the range 0.0 - 1.0
        Thread safe.
        """

    def update_progress_text(self, text: str) -> None:
        """
        Send a new progress text to the caller.
        Thread safe.
        """

class ProgressManager(AbstractProgressManager):
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...

class VoidProgressManager(AbstractProgressManager):
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
