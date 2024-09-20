from typing import Any, Callable, Generic, TypeVar, overload

from _typeshed import Incomplete

GetT = TypeVar("GetT")
SetT = TypeVar("SetT")

class TypedProperty(Generic[GetT, SetT]):
    """
    Type hinting with the vanilla property does not support having a different type on the setter.
    See https://github.com/python/mypy/issues/3004
    This is a custom property implementation that supports independently typing the getter and setter to appease mypy.

    Note that the getter, setter and deleter return the method they were given and not a property instance.
    This was to appease mypy complaining about overriding variables.
    This has a side effect that a setter can be used as a setter or the method

    >>> class MyClass:
    >>>     def __init__(self) -> None:
    >>>         self._value = 1
    >>>
    >>>     @TypedProperty[int, int | float]
    >>>     def value(self) -> int:
    >>>         return self._value
    >>>
    >>>     @value.setter
    >>>     def set_value(self, val: int | float) -> None:
    >>>         self._value = int(val)
    >>>
    >>>     @value.deleter
    >>>     def del_value(self) -> None:
    >>>         del self._value
    >>>
    >>>
    >>> inst = MyClass()
    >>> assert inst.value == 1
    >>> inst.value = 2
    >>> assert inst.value == 2
    >>> inst.set_value(3)
    >>> assert inst.value == 3
    >>> del inst.value
    >>> try:
    >>>     inst.value
    >>> except AttributeError:
    >>>     pass
    >>> else:
    >>>     raise Exception
    >>> inst.value = 4
    >>> assert inst.value == 4

    If you want the original methods to be private then just prefix them with an underscore.
    """

    fget: Callable[[Any], GetT] | None
    fset: Callable[[Any, SetT], None] | None
    fdel: Callable[[Any], None] | None
    __doc__: Incomplete
    def __init__(
        self,
        fget: Callable[[Any], GetT] | None = None,
        fset: Callable[[Any, SetT], None] | None = None,
        fdel: Callable[[Any], None] | None = None,
        doc: str | None = None,
    ) -> None: ...
    def __set_name__(self, owner: Any, name: str) -> None: ...
    @overload
    def __get__(self, obj: None, objtype: None) -> TypedProperty[GetT, SetT]: ...
    @overload
    def __get__(self, obj: object, objtype: type[object]) -> GetT: ...
    def __set__(self, obj: Any, value: SetT) -> None: ...
    def __delete__(self, obj: Any) -> None: ...
    def getter(self, fget: Callable[[Any], GetT]) -> Callable[[Any], GetT]: ...
    def setter(
        self, fset: Callable[[Any, SetT], None]
    ) -> Callable[[Any, SetT], None]: ...
    def deleter(self, fdel: Callable[[Any], None]) -> Callable[[Any], None]: ...
