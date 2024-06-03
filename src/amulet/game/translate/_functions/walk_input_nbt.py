from __future__ import annotations

from typing import Self, TypeVar, cast, Any
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
    Data,
    translation_function_from_json,
    follow_nbt_path,
)
from amulet.game.abc import JSONCompatible, JSONDict
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


KeyT = TypeVar("KeyT", str, int)


class WalkInputNBTOptions(AbstractBaseTranslationFunction):
    # Class variables
    Name = "_walk_input_nbt"
    _instances = {}

    # Instance variables
    _nbt_cls: type[CompoundTag] | type[ListTag]
    _self_default: AbstractBaseTranslationFunction | None
    _functions: AbstractBaseTranslationFunction | None
    _keys: FrozenMapping[str, WalkInputNBTOptions] | None
    _index: FrozenMapping[int, WalkInputNBTOptions] | None
    _nested_default: AbstractBaseTranslationFunction | None

    def __init__(
        self,
        nbt_cls: type[CompoundTag] | type[ListTag],
        self_default: AbstractBaseTranslationFunction | None = None,
        functions: AbstractBaseTranslationFunction | None = None,
        keys: Mapping[str, WalkInputNBTOptions] | None = None,
        index: Mapping[int, WalkInputNBTOptions] | None = None,
        nested_default: AbstractBaseTranslationFunction | None = None,
    ) -> None:
        super().__init__()
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

    def __reduce__(self) -> Any:
        return WalkInputNBTOptions, (
            self._nbt_cls,
            self._self_default,
            self._functions,
            self._keys,
            self._index,
            self._nested_default,
        )

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
            (
                translation_function_from_json(data["self_default"])
                if "self_default" in data
                else None
            ),
            (
                translation_function_from_json(data["functions"])
                if "functions" in data
                else None
            ),
            keys,
            index,
            (
                translation_function_from_json(data["nested_default"])
                if "nested_default" in data
                else None
            ),
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

        nbt = src.nbt
        if nbt is None:
            raise RuntimeError
        nbt_path_or_none = state.nbt_path
        if nbt_path_or_none is None:
            raise RuntimeError
        else:
            nbt_path = nbt_path_or_none

        tag_or_none = follow_nbt_path(nbt, nbt_path)

        nbt_cls = self._nbt_cls
        if tag_or_none is None:
            pass
        elif isinstance(tag_or_none, nbt_cls):
            tag = tag_or_none

            def run(
                keys: Iterable[KeyT],
                lut: Mapping[KeyT, WalkInputNBTOptions] | None,
                nested_dtype: NBTTagClsT | None,
            ) -> None:
                for key in keys:
                    if lut is not None and key in lut:
                        lut[key].run(src, StateData(), dst)
                    elif self._nested_default is not None:
                        outer_name, outer_type, path = nbt_path
                        new_type: NBTTagClsT
                        if nested_dtype is None:
                            new_type = tag.__class__
                        else:
                            new_type = nested_dtype
                        new_path: NBTPath = path + (
                            (
                                key,
                                new_type,
                            ),
                        )
                        self._nested_default.run(
                            src,
                            StateData(
                                state.relative_location,
                                (
                                    outer_name,
                                    outer_type,
                                    new_path,
                                ),
                            ),
                            dst,
                        )

            if isinstance(tag, CompoundTag):
                run(
                    [key for key in tag.keys() if isinstance(key, str)],
                    self._keys,
                    None,
                )
            elif isinstance(tag, ListTag):
                dtype = NBTLookUp[tag.element_tag_id]
                assert dtype is not None
                run(range(len(tag)), self._index, dtype)
            elif isinstance(tag, AbstractBaseArrayTag):
                nested_dtype_: NBTTagClsT
                if isinstance(tag, ByteArrayTag):
                    nested_dtype_ = ByteTag
                elif isinstance(tag, IntArrayTag):
                    nested_dtype_ = IntTag
                elif isinstance(tag, LongArrayTag):
                    nested_dtype_ = LongTag
                else:
                    raise TypeError
                run(range(len(tag)), self._index, nested_dtype_)
            else:
                return

        elif self._self_default is not None:
            self._self_default.run(src, state, dst)


class WalkInputNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "walk_input_nbt"
    _instances = {}

    # Instance variables
    _walk_nbt: WalkInputNBTOptions
    _path: NBTPath | None

    def __init__(
        self,
        walk_nbt: WalkInputNBTOptions,
        path: Sequence[NBTPathElement] | None = None,
    ) -> None:
        super().__init__()
        self._walk_nbt = walk_nbt
        self._path = None if path is None else tuple(path)

    def __reduce__(self) -> Any:
        return WalkInputNBT, (self._walk_nbt, self._path)

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
