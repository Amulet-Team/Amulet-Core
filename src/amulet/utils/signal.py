from __future__ import annotations

from typing import Protocol, TypeVarTuple
from collections.abc import Callable
from ._signal import ConnectionMode

Args = TypeVarTuple("Args")


class SignalToken(Protocol[*Args]):
    pass


class Signal(Protocol[*Args]):
    def connect(
        self,
        callback: Callable[[*Args], None],
        mode: ConnectionMode = ConnectionMode.Direct,
    ) -> SignalToken[*Args]:
        """
        Connect a callback to this signal and return a token.
        The token returned can be used to disconnect the callback.
        """

    def disconnect(self, token: SignalToken[*Args]) -> None:
        """
        Disconnect a callback.
        Token is the value returned by connect.
        """

    def emit(self, *args: *Args) -> None:
        """
        Call all callbacks with the given arguments from this thread.
        Blocks until all callbacks are processed.
        """
