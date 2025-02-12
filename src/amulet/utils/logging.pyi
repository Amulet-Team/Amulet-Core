from __future__ import annotations

import amulet.utils.signal

__all__ = [
    "get_default_log_level",
    "get_logger",
    "register_default_log_handler",
    "set_default_log_level",
    "unregister_default_log_handler",
]

def get_default_log_level() -> int: ...
def get_logger() -> amulet.utils.signal.Signal[int, str]: ...
def register_default_log_handler() -> None: ...
def set_default_log_level(level: int) -> None: ...
def unregister_default_log_handler() -> None: ...
