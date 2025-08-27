from __future__ import annotations

import collections.abc

__all__: list[str] = ["get_tests"]

def get_tests() -> list[collections.abc.Callable[[], None]]: ...
