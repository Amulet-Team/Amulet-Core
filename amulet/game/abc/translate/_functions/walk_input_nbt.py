from __future__ import annotations

from typing import Self
from collections.abc import Mapping, Sequence

from amulet_nbt import CompoundTag, ListTag

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    Data,
    StrToNBTCls,
    NBTClsToStr,
    from_json,
    NBTTagClsT,
)
from ._frozen import FrozenMapping


class WalkInputNBTOptions(AbstractBaseTranslationFunction):
    # Class variables
    Name = "_walk_input_nbt"
    _instances: dict[WalkInputNBTOptions, WalkInputNBTOptions] = {}

    # Instance variables
    _nbt_cls: type[CompoundTag] | type[ListTag]
    _self_default: AbstractBaseTranslationFunction | None
    _functions: AbstractBaseTranslationFunction | None
    _keys: FrozenMapping[str, WalkInputNBTOptions] | None
    _index: FrozenMapping[int, WalkInputNBTOptions] | None
    _nested_default: AbstractBaseTranslationFunction | None

    def __new__(
        cls,
        nbt_cls: type[CompoundTag] | type[ListTag],
        self_default: AbstractBaseTranslationFunction | None = None,
        functions: AbstractBaseTranslationFunction | None = None,
        keys: Mapping[str, WalkInputNBTOptions] | None = None,
        index: Mapping[int, WalkInputNBTOptions] | None = None,
        nested_default: AbstractBaseTranslationFunction | None = None,
    ) -> WalkInputNBTOptions:
        self = super().__new__(cls)
        self._nbt_cls = nbt_cls
        self._self_default = self_default
        self._functions = functions
        self._keys = (
            None if keys is None else FrozenMapping[str, WalkInputNBTOptions](keys)
        )
        self._index = (
            None if index is None else FrozenMapping[int, WalkInputNBTOptions](index)
        )
        self._nested_default = nested_default
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return (
            self._nbt_cls,
            self._self_default,
            self._functions,
            self._keys,
            self._index,
            self._nested_default,
        )

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        nbt_type = data["type"]
        assert isinstance(nbt_type, str)
        if "keys" in data:
            raw_keys = data["keys"]
            assert isinstance(raw_keys, dict)
            keys = {
                key: WalkInputNBTOptions.from_json(value)
                for key, value in raw_keys.items()
            }
        else:
            keys = None
        if "index" in data:
            raw_index = data["index"]
            assert isinstance(raw_index, dict)
            index = {
                int(key): WalkInputNBTOptions.from_json(value)
                for key, value in raw_index.items()
            }
        else:
            index = None
        return cls(
            StrToNBTCls[nbt_type],
            from_json(data["self_default"]) if "self_default" in data else None,
            from_json(data["functions"]) if "functions" in data else None,
            keys,
            index,
            from_json(data["nested_default"]) if "nested_default" in data else None,
        )

    def to_json(self) -> JSONDict:
        options: JSONDict = {
            "type": NBTClsToStr[self._nbt_cls],
        }
        if self._self_default is not None:
            options["self_default"] = self._self_default.to_json()
        if self._functions is not None:
            options["functions"] = self._functions.to_json()
        if self._keys is not None:
            options["keys"] = {
                key: value.to_json() for key, value in self._keys.items()
            }
        if self._index is not None:
            options["index"] = {
                str(key): value.to_json() for key, value in self._index.items()
            }
        if self._nested_default is not None:
            options["nested_default"] = self._nested_default.to_json()
        return options

    def run(self, *args, **kwargs):
        pass


class WalkInputNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "walk_input_nbt"
    _instances: dict[WalkInputNBT, WalkInputNBT] = {}

    # Instance variables
    _walk_nbt: WalkInputNBTOptions
    _path: tuple[tuple[str | int, NBTTagClsT], ...] | None

    def __new__(
        cls,
        walk_nbt: WalkInputNBTOptions,
        path: Sequence[tuple[str | int, NBTTagClsT]] | None = None,
    ) -> WalkInputNBT:
        self = super().__new__(cls)
        self._walk_nbt = walk_nbt
        self._path = None if path is None else tuple(path)
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._walk_nbt, self._path

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "walk_input_nbt"
        raw_path = data.get("path", None)
        if raw_path is None:
            path = None
        elif isinstance(raw_path, list):
            path = tuple((key, StrToNBTCls[cls_name]) for key, cls_name in raw_path)
        else:
            raise TypeError
        return cls(
            WalkInputNBTOptions.from_json(data["options"]),
            path,
        )

    def to_json(self) -> JSONDict:
        data: JSONDict = {
            "function": "walk_input_nbt",
            "options": self._walk_nbt.to_json(),
        }
        if self._path is not None:
            data["path"] = [[key, NBTClsToStr[cls]] for key, cls in self._path]
        return data

    def run(self, *args, **kwargs):
        pass
