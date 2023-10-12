from __future__ import annotations

import logging
from typing import Optional, Union, Callable, Any, overload, Protocol, TYPE_CHECKING
from weakref import WeakMethod
from inspect import ismethod


if TYPE_CHECKING:
    import PySide6.QtCore  # noqa


class SignalInstance(Protocol):
    def connect(
        self,
        slot: Union[Callable, SignalInstance],
        type: Union[None, PySide6.QtCore.Qt.ConnectionType] = ...,
    ):
        ...

    def disconnect(self, slot: Optional[Union[Callable, SignalInstance]] = None):
        ...

    def emit(self, *args: Any):
        ...


_signal_instance_constructor: Optional[SignalInstanceConstructor] = None


def create_signal_instance(
    *,
    types: tuple[type, ...],
    name: Optional[str],
    arguments: Optional[str],
    instance: Any,
) -> SignalInstance:
    """Create a new signal instance"""
    if _signal_instance_constructor is None:
        set_signal_instance_constructor(get_fallback_signal_instance_constructor())
    return _signal_instance_constructor(
        types=types,
        name=name,
        arguments=arguments,
        instance=instance,
    )


SignalInstanceCacheName = "_SignalCache"


def _get_signal_instances(instance) -> dict:
    try:
        signal_instances = getattr(instance, SignalInstanceCacheName)
    except AttributeError:
        signal_instances = {}
        setattr(instance, SignalInstanceCacheName, signal_instances)
    return signal_instances


class Signal:
    def __init__(
        self, *types: type, name: Optional[str] = "", arguments: Optional[str] = ()
    ):
        self._types = types
        self._name = name
        self._arguments = arguments

    @overload
    def __get__(self, instance: None, owner: Optional[Any]) -> Signal:
        ...

    @overload
    def __get__(self, instance: Any, owner: Optional[Any]) -> SignalInstance:
        ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        signal_instances = _get_signal_instances(instance)
        if self not in signal_instances:
            signal_instances[self] = create_signal_instance(
                types=self._types,
                name=self._name,
                arguments=self._arguments,
                instance=instance,
            )
        return signal_instances[self]


class SignalInstanceConstructor(Protocol):
    def __call__(
        self,
        *,
        types: tuple[type, ...],
        name: Optional[str],
        arguments: Optional[str],
        instance: Any,
    ) -> SignalInstance:
        ...


def set_signal_instance_constructor(constructor: SignalInstanceConstructor):
    global _signal_instance_constructor
    if _signal_instance_constructor is not None:
        raise RuntimeError("Signal instance constructor has already been set.")
    _signal_instance_constructor = constructor


def get_fallback_signal_instance_constructor() -> SignalInstanceConstructor:
    class FallbackSignalInstance:
        def __init__(self, *types: type):
            self._types = types
            self._callbacks: set[
                Union[Callable, WeakMethod, FallbackSignalInstance]
            ] = set()

        @staticmethod
        def _wrap_slot(slot: Union[Callable, FallbackSignalInstance]):
            if ismethod(slot):
                return WeakMethod(slot)
            elif isinstance(slot, FallbackSignalInstance) or callable(slot):
                return slot
            else:
                raise RuntimeError(f"{slot} is not a supported slot type.")

        def connect(self, slot: Union[Callable, FallbackSignalInstance], type=None):
            if type is not None:
                logging.warning(
                    "FallbackSignalInstance does not support custom connection types. Using DirectConnection"
                )
            self._callbacks.add(self._wrap_slot(slot))

        def disconnect(self, slot: Union[Callable, FallbackSignalInstance] = None):
            self._callbacks.remove(self._wrap_slot(slot))

        def emit(self, *args: Any):
            if len(args) != len(self._types):
                raise TypeError(
                    f"SignalInstance{self._types}.emit expected {len(self._types)} argument(s), {len(args)} given."
                )
            for slot in self._callbacks:
                try:
                    if isinstance(slot, FallbackSignalInstance):
                        slot.emit(*args)
                    elif isinstance(slot, WeakMethod):
                        slot = slot()
                        if slot is not None:
                            slot(*args)
                    else:
                        slot(*args)
                except Exception as e:
                    logging.error(e)

    def fallback_signal_instance_constructor(
        *,
        types: tuple[type, ...],
        name: Optional[str],
        arguments: Optional[str],
        instance: Any,
    ) -> FallbackSignalInstance:
        return FallbackSignalInstance(*types)

    return fallback_signal_instance_constructor


def get_pyside6_signal_instance_constructor() -> SignalInstanceConstructor:
    try:
        from PySide6.QtCore import (
            QObject,
            Signal as PySide6_Signal,
            SignalInstance as PySide6_SignalInstance,
        )
    except ImportError as e:
        raise ImportError("Could not import PySide6") from e

    QObjectCacheName = "_QObjectCache"

    def pyside6_signal_instance_constructor(
        *,
        types: tuple[type, ...],
        name: Optional[str],
        arguments: Optional[str],
        instance: Any,
    ) -> PySide6_SignalInstance:
        if isinstance(instance, QObject):
            return PySide6_Signal(*types, name=name, arguments=arguments).__get__(
                instance, QObject
            )
        else:
            signal_instances = _get_signal_instances(instance)
            if QObjectCacheName not in signal_instances:
                signal_instances[QObjectCacheName] = QObject
            obj = signal_instances[QObjectCacheName]
            if not isinstance(obj, QObject):
                raise RuntimeError
            return PySide6_Signal(*types, name=name, arguments=arguments).__get__(
                obj, QObject
            )

    return pyside6_signal_instance_constructor
