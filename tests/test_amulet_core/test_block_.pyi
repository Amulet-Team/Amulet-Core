from __future__ import annotations

import collections.abc

__all__: list[str] = ["get_block_stack_tests", "get_block_tests"]

def get_block_stack_tests() -> list[tuple[str, collections.abc.Callable[[], None]]]: ...
def get_block_tests() -> list[tuple[str, collections.abc.Callable[[], None]]]: ...
