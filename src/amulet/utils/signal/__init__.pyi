from __future__ import annotations

from amulet.utils.signal._signal import (
    Signal,
    SignalInstance,
    SignalInstanceConstructor,
    create_signal_instance,
    get_fallback_signal_instance_constructor,
    get_pyside6_signal_instance_constructor,
    set_signal_instance_constructor,
)

from . import _signal

__all__ = [
    "Signal",
    "SignalInstance",
    "SignalInstanceCacheName",
    "SignalInstanceConstructor",
    "create_signal_instance",
    "get_fallback_signal_instance_constructor",
    "get_pyside6_signal_instance_constructor",
    "set_signal_instance_constructor",
]
SignalInstanceCacheName: str
