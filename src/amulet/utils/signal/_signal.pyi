from collections.abc import Sequence
from typing import Any, Callable, Generic, Protocol, TypeVarTuple, overload

import PySide6.QtCore

CallArgs = TypeVarTuple("CallArgs")

class SignalInstance(Protocol[*CallArgs]):
    def connect(
        self,
        slot: (
            Callable[[Unpack[CallArgs]], None] | SignalInstance[Unpack[CallArgs]] | None
        ),
        type: PySide6.QtCore.Qt.ConnectionType | None = ...,
    ) -> None: ...
    def disconnect(
        self,
        slot: (
            Callable[[Unpack[CallArgs]], None] | SignalInstance[Unpack[CallArgs]] | None
        ) = None,
    ) -> None: ...
    def emit(self, *args: Unpack[CallArgs]) -> None: ...

def create_signal_instance(
    *types: type, instance: Any, name: str, arguments: Sequence[str] = ()
) -> SignalInstance[Unpack[CallArgs]]:
    """Create a new signal instance"""

SignalInstanceCacheName: str

class Signal(Generic[*CallArgs]):
    def __init__(
        self, *types: type, name: str, arguments: Sequence[str] = ()
    ) -> None: ...
    @overload
    def __get__(
        self, instance: None, owner: Any | None
    ) -> Signal[Unpack[CallArgs]]: ...
    @overload
    def __get__(
        self, instance: Any, owner: Any | None
    ) -> SignalInstance[Unpack[CallArgs]]: ...

class SignalInstanceConstructor(Protocol[*CallArgs]):
    def __call__(
        self,
        *,
        types: tuple[type, ...],
        name: str,
        arguments: Sequence[str],
        instance: Any,
    ) -> SignalInstance[Unpack[CallArgs]]: ...

def set_signal_instance_constructor(constructor: SignalInstanceConstructor) -> None: ...
def get_fallback_signal_instance_constructor() -> SignalInstanceConstructor: ...
def get_pyside6_signal_instance_constructor() -> SignalInstanceConstructor: ...
