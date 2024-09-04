from __future__ import annotations
from amulet.utils.signal._signal import Signal
from amulet.utils.signal._signal import SignalInstance
from amulet.utils.signal._signal import SignalInstanceConstructor
from amulet.utils.signal._signal import create_signal_instance
from amulet.utils.signal._signal import get_fallback_signal_instance_constructor
from amulet.utils.signal._signal import get_pyside6_signal_instance_constructor
from amulet.utils.signal._signal import set_signal_instance_constructor
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
SignalInstanceCacheName: str = "_SignalCache"
