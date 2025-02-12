from __future__ import annotations

import amulet.utils.signal

__all__ = ["get_logger", "unregister_default_log_handler"]

def get_logger() -> amulet.utils.signal.Signal[int, str]: ...
def unregister_default_log_handler() -> None: ...
