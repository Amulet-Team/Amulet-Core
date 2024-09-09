from __future__ import annotations

import logging as logging
import typing
from collections.abc import Sequence
from inspect import ismethod
from typing import Any, Generic, Protocol, TypeVarTuple, overload
from weakref import WeakMethod

__all__ = [
    "Any",
    "CallArgs",
    "Generic",
    "Protocol",
    "Sequence",
    "Signal",
    "SignalInstance",
    "SignalInstanceCacheName",
    "SignalInstanceConstructor",
    "TypeVarTuple",
    "WeakMethod",
    "create_signal_instance",
    "get_fallback_signal_instance_constructor",
    "get_pyside6_signal_instance_constructor",
    "ismethod",
    "logging",
    "overload",
    "set_signal_instance_constructor",
]

class Signal(typing.Generic):
    def __get__(self, instance: typing.Any, owner: typing.Any) -> typing.Any: ...
    def __init__(
        self, *types: type, name: str, arguments: typing.Sequence[str] = tuple()
    ): ...

class SignalInstance(typing.Protocol):
    @classmethod
    def __subclasshook__(cls, other): ...
    def __init__(self, *args, **kwargs): ...
    def connect(
        self,
        slot: typing.Callable[[*CallArgs], None] | SignalInstance[*CallArgs,] | None,
        type: PySide6.QtCore.Qt.ConnectionType | None = ...,
    ) -> None: ...
    def disconnect(
        self,
        slot: (
            typing.Callable[[*CallArgs], None] | SignalInstance[*CallArgs,] | None
        ) = None,
    ) -> None: ...
    def emit(self, *args: *CallArgs) -> None: ...

class SignalInstanceConstructor(typing.Protocol):
    @classmethod
    def __subclasshook__(cls, other): ...
    def __call__(
        self,
        *,
        types: tuple[type, ...],
        name: str,
        arguments: typing.Sequence[str],
        instance: typing.Any,
    ) -> SignalInstance[*CallArgs,]: ...
    def __init__(self, *args, **kwargs): ...

def _get_signal_instances(instance: typing.Any) -> dict[Signal, SignalInstance]: ...
def create_signal_instance(
    *types: type,
    instance: typing.Any,
    name: str,
    arguments: typing.Sequence[str] = tuple(),
) -> SignalInstance[*CallArgs,]:
    """
    Create a new signal instance
    """

def get_fallback_signal_instance_constructor() -> SignalInstanceConstructor: ...
def get_pyside6_signal_instance_constructor() -> SignalInstanceConstructor: ...
def set_signal_instance_constructor(constructor: SignalInstanceConstructor) -> None: ...

CallArgs: typing.TypeVarTuple  # value = CallArgs
SignalInstanceCacheName: str
_signal_instance_constructor = None
