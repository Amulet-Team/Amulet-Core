from __future__ import annotations

from typing import Protocol, TypeVarTuple
from collections.abc import Callable

Args = TypeVarTuple("Args")


class SignalToken(Protocol[*Args]):
    pass


class Signal(Protocol[*Args]):
    def connect(self, callback: Callable[[*Args], None]) -> SignalToken[*Args]: ...

    def disconnect(self, token: SignalToken[*Args]) -> None: ...

    def emit(self, *args: *Args) -> None: ...
