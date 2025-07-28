from __future__ import annotations

import collections.abc

__all__ = ["get_tests"]

def get_tests() -> list[tuple[str, collections.abc.Callable[[], None]]]: ...
