from __future__ import annotations

from typing import Any, Protocol, cast
from abc import ABC, abstractmethod

from amulet_nbt import (
    from_snbt,
    NamedTag,
    CompoundTag,
    ListTag,
)

from amulet.block import PropertyValueType, PropertyValueClasses
from ..._json_interface import JSONInterface, JSONCompatible, JSONDict, JSONList
from ._state import SrcData, StateData, DstData
from ._typing import NBTPath, NBTTagT


def immutable_from_snbt(snbt: str) -> PropertyValueType:
    val = from_snbt(snbt)
    assert isinstance(val, PropertyValueClasses)
    return val


def follow_nbt_path(
    nbt: NamedTag, nbt_path: tuple[str, type[CompoundTag] | type[ListTag], NBTPath]
) -> NBTTagT | None:
    outer_name, outer_type, path = nbt_path
    if nbt.name != outer_name or not isinstance(nbt.tag, outer_type):
        return None
    tag = nbt.tag
    for key, tag_cls in path:
        if isinstance(key, int) and isinstance(tag, ListTag) and key < len(tag):
            tag = tag[key]
        elif isinstance(key, str) and isinstance(tag, CompoundTag) and key in tag:
            tag = tag[key]
        else:
            return None
        if not isinstance(tag, tag_cls):
            return None
    return cast(NBTTagT | None, tag)


def translation_function_from_json(
    data: JSONCompatible,
) -> AbstractBaseTranslationFunction:
    if isinstance(data, list):
        func_cls = _translation_functions["sequence"]
        return func_cls.from_json(data)
    elif isinstance(data, dict):
        function_name = data["function"]
        assert isinstance(function_name, str)
        func_cls = _translation_functions[function_name]
        return func_cls.from_json(data)
    else:
        raise TypeError


_translation_functions: dict[str, type[AbstractBaseTranslationFunction]] = {}


class Data(Protocol):
    def __hash__(self) -> int: ...

    def __eq__(self, other: Any) -> bool: ...


class AbstractBaseTranslationFunction(JSONInterface, ABC):
    Name: str = ""
    _hash: int | None

    def __new__(cls) -> AbstractBaseTranslationFunction:
        self = super().__new__(cls)
        self._hash = None
        return self

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if cls.Name == "":
            raise RuntimeError(f"Name attribute has not been set for {cls}")
        if cls.Name in _translation_functions:
            raise RuntimeError(
                f"A translation function with name {cls.Name} already exists."
            )
        _translation_functions[cls.Name] = cls

    @abstractmethod
    def __reduce__(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def _data(self) -> Data:
        raise NotImplementedError

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._data())
        return self._hash

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._data() == other._data()

    @abstractmethod
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        """Run the translation function"""
        raise NotImplementedError
