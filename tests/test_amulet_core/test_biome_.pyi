from __future__ import annotations

import typing

__all__ = ["get_tests"]

def get_tests() -> list[tuple[str, typing.Callable[[], None]]]: ...
