from __future__ import annotations

from typing import Protocol, TypeVarTuple, runtime_checkable
from collections.abc import Callable
from ._signal import ConnectionMode

Args = TypeVarTuple("Args")


class SignalToken(Protocol[*Args]):
    pass


@runtime_checkable
class Signal(Protocol[*Args]):
    def connect(
        self,
        callback: Callable[[*Args], None],
        mode: ConnectionMode = ConnectionMode.Direct,
    ) -> SignalToken[*Args]:
        """
        Connect a callback to this signal and return a token.
        The token must be kept alive for the callback to work.
        The token is used to disconnect the callback when it is not needed.
        Thread safe.
        """

    def disconnect(self, token: SignalToken[*Args]) -> None:
        """
        Disconnect a callback.
        Token is the value returned by connect.
        Thread safe.
        """

    def emit(self, *args: *Args) -> None:
        """
        Call all callbacks with the given arguments from this thread.
        Blocks until all callbacks are processed.
        Thread safe.
        """
