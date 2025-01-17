from __future__ import annotations

import typing

__all__ = ["AbstractProgressManager", "ProgressManager", "VoidProgressManager"]

class AbstractProgressManager:
    def get_child(
        self, progress_min: float, progress_max: float
    ) -> AbstractProgressManager: ...
    def register_progress_callback(
        self, callback: typing.Callable[[float], None]
    ) -> None: ...
    def register_progress_text_callback(
        self, callback: typing.Callable[[str], None]
    ) -> None: ...
    def unregister_progress_callback(
        self, callback: typing.Callable[[float], None]
    ) -> None: ...
    def unregister_progress_text_callback(
        self, callback: typing.Callable[[str], None]
    ) -> None: ...
    def update_progress(self, progress: float) -> None: ...
    def update_progress_text(self, text: str) -> None: ...

class ProgressManager(AbstractProgressManager):
    @staticmethod
    def __repr__() -> str: ...
    def __init__(self) -> None: ...

class VoidProgressManager(AbstractProgressManager):
    @staticmethod
    def __repr__() -> str: ...
    def __init__(self) -> None: ...

class _ProgressManager(AbstractProgressManager):
    pass
