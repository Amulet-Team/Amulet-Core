from threading import Lock
from weakref import WeakValueDictionary
from typing import Generic, TypeVar

from amulet.utils.signal import SignalInstance, create_signal_instance


T = TypeVar("T")


class SignalMap(Generic[T]):
    """
    A map from keys to a weakly referenced signal instance per key.
    This is useful if you want a signal instance for individual resources.
    """

    def __init__(self, *types: type, name: str = "", arguments: list[str] = ()):
        """
        Construct a new SignalMap instance.
        :param types: The types to pass to the signals.
        :param name: The name to pass to the signals.
        :param arguments: The arguments to pass to the signals.
        """
        self._lock = Lock()
        self._signals: WeakValueDictionary[T, SignalInstance] = WeakValueDictionary()
        self._types = types
        self._name = name
        self._arguments = arguments

    def get(self, key: T) -> SignalInstance:
        """
        Get the signal instance for the requested key.
        The returned SignalInstance must be strongly stored until the caller is finished with it otherwise the slots may
        not be executed. When finished, the caller must disconnect the slots it connected.
        :param key: The key to get the signal instance for.
        :return:
        """
        with self._lock:
            signal = self._signals.get(key)
            if signal is None:
                signal = self._signals[key] = create_signal_instance(
                    *self._types,
                    instance=self,
                    name=self._name,
                    arguments=self._arguments
                )
            return signal

    def emit(self, key: T, *args):
        """Emit from the signal if it exists."""
        signal = self._signals.get(key)
        if signal is not None:
            signal.emit(*args)
