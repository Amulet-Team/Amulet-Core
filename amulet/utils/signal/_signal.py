from __future__ import annotations

import logging
from typing import (
    Callable,
    Any,
    overload,
    Protocol,
    TYPE_CHECKING,
    TypeVarTuple,
    Generic,
)
from collections.abc import Sequence
from weakref import WeakMethod
from inspect import ismethod


if TYPE_CHECKING:
    import PySide6.QtCore  # type: ignore  # noqa


CallArgs = TypeVarTuple("CallArgs")


class SignalInstance(Protocol[*CallArgs]):
    def connect(
        self,
        slot: Callable[[*CallArgs], None] | SignalInstance[*CallArgs] | None,
        type: PySide6.QtCore.Qt.ConnectionType | None = ...,
    ) -> None: ...

    def disconnect(
        self,
        slot: Callable[[*CallArgs], None] | SignalInstance[*CallArgs] | None = None,
    ) -> None: ...

    def emit(self, *args: *CallArgs) -> None: ...


_signal_instance_constructor: SignalInstanceConstructor | None = None


# TODO: https://github.com/python/typing/issues/1216


def create_signal_instance(
    *types: type, instance: Any, name: str = "", arguments: Sequence[str] = ()
) -> SignalInstance[*CallArgs]:
    """Create a new signal instance"""
    if _signal_instance_constructor is None:
        set_signal_instance_constructor(get_fallback_signal_instance_constructor())
        assert _signal_instance_constructor is not None
    return _signal_instance_constructor(
        types=types,
        name=name,
        arguments=arguments,
        instance=instance,
    )


SignalInstanceCacheName = "_SignalCache"


def _get_signal_instances(instance: Any) -> dict[Signal, SignalInstance]:
    signal_instances: dict[Any, SignalInstance]
    try:
        signal_instances = getattr(instance, SignalInstanceCacheName)
    except AttributeError:
        signal_instances = {}
        setattr(instance, SignalInstanceCacheName, signal_instances)
    return signal_instances


class Signal(Generic[*CallArgs]):
    def __init__(self, *types: type, name: str = "", arguments: Sequence[str] = ()):
        self._types = types
        self._name = name
        self._arguments = arguments

    @overload
    def __get__(self, instance: None, owner: Any | None) -> Signal[*CallArgs]: ...

    @overload
    def __get__(
        self, instance: Any, owner: Any | None
    ) -> SignalInstance[*CallArgs]: ...

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self
        signal_instances = _get_signal_instances(instance)
        if self not in signal_instances:
            signal_instances[self] = create_signal_instance(
                *self._types,
                name=self._name,
                arguments=self._arguments,
                instance=instance,
            )
        return signal_instances[self]


class SignalInstanceConstructor(Protocol[*CallArgs]):
    def __call__(
        self,
        *,
        types: tuple[type, ...],
        name: str,
        arguments: Sequence[str],
        instance: Any,
    ) -> SignalInstance[*CallArgs]: ...


def set_signal_instance_constructor(constructor: SignalInstanceConstructor) -> None:
    global _signal_instance_constructor
    if _signal_instance_constructor is not None:
        raise RuntimeError("Signal instance constructor has already been set.")
    _signal_instance_constructor = constructor


def get_fallback_signal_instance_constructor() -> SignalInstanceConstructor:
    class FallbackSignalInstance(SignalInstance[*CallArgs]):
        _callbacks: set[
            Callable[[*CallArgs], None]
            | WeakMethod[Callable[[*CallArgs], None]]
            | FallbackSignalInstance[*CallArgs]
        ]

        def __init__(self, *types: type):
            self._types = types
            self._callbacks = set()

        @staticmethod
        def _wrap_slot(
            slot: Callable[[*CallArgs], None] | SignalInstance[*CallArgs] | None
        ) -> (
            Callable[[*CallArgs], None]
            | WeakMethod[Callable[[*CallArgs], None]]
            | FallbackSignalInstance[*CallArgs]
        ):
            if ismethod(slot):
                return WeakMethod(slot)  # type: ignore
            elif isinstance(slot, FallbackSignalInstance) or callable(slot):
                return slot  # type: ignore
            else:
                raise RuntimeError(f"{slot} is not a supported slot type.")

        def connect(
            self,
            slot: Callable[[*CallArgs], None] | SignalInstance[*CallArgs] | None,
            type: PySide6.QtCore.Qt.ConnectionType | None = None,
        ) -> None:
            if type is not None:
                logging.warning(
                    "FallbackSignalInstance does not support custom connection types. Using DirectConnection"
                )
            self._callbacks.add(self._wrap_slot(slot))

        def disconnect(
            self,
            slot: Callable[[*CallArgs], None] | SignalInstance[*CallArgs] | None = None,
        ) -> None:
            self._callbacks.remove(self._wrap_slot(slot))

        def emit(self, *args: *CallArgs) -> None:
            if len(args) != len(self._types):
                raise TypeError(
                    f"SignalInstance{self._types}.emit expected {len(self._types)} argument(s), {len(args)} given."
                )
            for slot in self._callbacks:
                try:
                    if isinstance(slot, FallbackSignalInstance):
                        slot.emit(*args)  # type: ignore
                    elif isinstance(slot, WeakMethod):
                        method = slot()
                        if method is not None:
                            method(*args)
                    else:
                        slot(*args)
                except Exception as e:
                    logging.error(e)

    def fallback_signal_instance_constructor(
        *,
        types: tuple[type, ...],
        name: str,
        arguments: Sequence[str],
        instance: Any,
    ) -> FallbackSignalInstance[*CallArgs]:
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
        name: str,
        arguments: Sequence[str],
        instance: Any,
    ) -> PySide6_SignalInstance:
        if isinstance(instance, QObject):
            return PySide6_Signal(
                *types, name=name, arguments=list(arguments) if arguments else None
            ).__get__(instance, QObject)
        else:
            signal_instances = _get_signal_instances(instance)
            if QObjectCacheName not in signal_instances:
                signal_instances[QObjectCacheName] = QObject()  # type: ignore
            obj = signal_instances[QObjectCacheName]  # type: ignore
            if not isinstance(obj, QObject):
                raise RuntimeError
            return PySide6_Signal(*types, name=name, arguments=arguments).__get__(
                obj, QObject
            )

    return pyside6_signal_instance_constructor  # type: ignore
