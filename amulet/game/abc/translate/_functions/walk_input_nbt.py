from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping, Sequence, Iterable
import logging

from amulet_nbt import (
    AbstractBaseArrayTag,
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    FloatTag,
    DoubleTag,
    ByteArrayTag,
    StringTag,
    ListTag,
    CompoundTag,
    IntArrayTag,
    LongArrayTag,
)

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    Data,
    from_json,
    follow_nbt_path,
)
from ._typing import NBTClsToStr, StrToNBTCls, NBTPath, NBTPathElement, NBTTagClsT
from ._frozen import FrozenMapping
from ._state import SrcData, StateData, DstData

log = logging.getLogger(__name__)


NBTLookUp = [
    None,
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    FloatTag,
    DoubleTag,
    ByteArrayTag,
    StringTag,
    ListTag,
    CompoundTag,
    IntArrayTag,
    LongArrayTag,
]


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

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        if self._functions is not None:
            self._functions.run(src, state, dst)

        assert src.nbt is not None and state.nbt_path is not None
        nbt = follow_nbt_path(src.nbt, state.nbt_path)

        nbt_cls = self._nbt_cls
        if isinstance(nbt, nbt_cls):
            keys: Iterable[Any]
            lut: Mapping[Any, WalkInputNBTOptions] | None
            nested_dtype: NBTTagClsT | None
            if isinstance(nbt, CompoundTag):
                keys = nbt.keys()
                lut = self._keys
                nested_dtype = None
            elif isinstance(nbt, ListTag):
                keys = range(len(nbt))
                lut = self._index
                nested_dtype = NBTLookUp[nbt.list_data_type]
            elif isinstance(nbt, AbstractBaseArrayTag):
                keys = range(len(nbt))
                lut = self._index
                if isinstance(nbt, ByteArrayTag):
                    nested_dtype = ByteTag
                elif isinstance(nbt, IntArrayTag):
                    nested_dtype = IntTag
                elif isinstance(nbt, LongArrayTag):
                    nested_dtype = LongTag
                else:
                    raise TypeError
            else:
                return

            for key in keys:
                if lut is not None and key in lut:
                    lut[key].run(src, StateData(), dst)
                elif self._nested_default is not None and key in self._nested_default:
                    outer_name, outer_type, path = state.nbt_path
                    new_dtype = nbt.__class__ if nested_dtype is None else nested_dtype
                    self._nested_default.run(
                        src,
                        StateData(
                            state.relative_location,
                            (outer_name, outer_type, path + ((key, new_dtype),)),
                        ),
                        dst,
                    )

        elif self._self_default is not None:
            self._self_default.run(src, state, dst)


class WalkInputNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "walk_input_nbt"
    _instances: dict[WalkInputNBT, WalkInputNBT] = {}

    # Instance variables
    _walk_nbt: WalkInputNBTOptions
    _path: NBTPath | None

    def __new__(
        cls,
        walk_nbt: WalkInputNBTOptions,
        path: Sequence[NBTPathElement] | None = None,
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
            path = []
            for item in raw_path:
                assert isinstance(item, list) and len(item) == 2
                key, cls_name = item
                assert isinstance(key, str | int)
                assert isinstance(cls_name, str)
                path.append((key, StrToNBTCls[cls_name]))
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

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.cacheable = False
        nbt = src.nbt
        if nbt is None:
            dst.extra_needed = True
            return

        if self._path is None:
            new_state = state
        else:
            path = ("", CompoundTag, self._path)
            # verify that the data exists at the path
            tag = follow_nbt_path(nbt, path)
            if not isinstance(tag, self._path[-1][1]):
                log.error(f"Tag at path {path} does not exist or has the wrong type.")
                return
            new_state = StateData(state.relative_location, path)

        self._walk_nbt.run(src, new_state, dst)
