from __future__ import annotations

import amulet.utils.signal

__all__ = [
    "get_default_log_level",
    "get_logger",
    "register_default_log_handler",
    "set_default_log_level",
    "unregister_default_log_handler",
]

def get_default_log_level() -> int:
    """
    Get the log level used by the default logger.
    The default logger will only log messages with a level at least this large.
    Thread safe.
    """

def get_logger() -> amulet.utils.signal.Signal[int, str]:
    """
    Get the logger signal.
    This is emitted with the message and its level every time a message is logged.
    """

def register_default_log_handler() -> None:
    """
    Register the default log handler.
    This is registered by default with a log level of 20.
    Thread safe.
    """

def set_default_log_level(level: int) -> None:
    """
    Set the log level used by the default logger.
    The default logger will only log messages with a level at least this large.
    Thread safe.
    """

def unregister_default_log_handler() -> None:
    """
    Unregister the default log handler.
    Thread safe.
    """
