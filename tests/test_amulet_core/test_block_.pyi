from __future__ import annotations

import typing

__all__ = ["get_block_stack_tests", "get_block_tests"]

def get_block_stack_tests() -> list[tuple[str, typing.Callable[[], None]]]: ...
def get_block_tests() -> list[tuple[str, typing.Callable[[], None]]]: ...
