from __future__ import annotations

from typing import (
    Sequence,
    Self,
    Any,
)

from amulet_nbt import (
    ListTag,
    CompoundTag,
    read_snbt,
)

from .abc import (
    AbstractBaseTranslationFunction,
    Data,
)
from amulet.game.abc import JSONCompatible, JSONDict
from ._typing import (
    NBTTagT,
    NBTTagClasses,
    NBTClsToStr,
    StrToNBTCls,
    NBTPath,
    NBTPathElement,
)
from ._state import SrcData, StateData, DstData


class NewNBTItem(AbstractBaseTranslationFunction):
    # Class variables
    Name = "_new_nbt"
    _instances = {}

    # Instance variables
    _key: str | int
    _value: NBTTagT
    _snbt: str
    _outer_name: str
    _outer_type: type[CompoundTag] | type[ListTag]
    _path: NBTPath | None

    def __init__(
        self,
        key: str | int,
        value: NBTTagT,
        outer_name: str = "",
        outer_type: type[CompoundTag] | type[ListTag] = CompoundTag,
        path: (
            Sequence[tuple[str | int, type[CompoundTag] | type[ListTag]]] | None
        ) = None,
    ) -> None:
        super().__init__()
        assert isinstance(outer_name, str)
        self._outer_name = outer_name

        assert outer_type in NBTClsToStr
        self._outer_type = outer_type
        last_cls = outer_type

        if path is None:
            self._path = None
        else:
            path_l = list(path)
            for i, (path_key, nbt_cls) in enumerate(path_l):
                assert nbt_cls is CompoundTag or nbt_cls is ListTag
                assert (last_cls is CompoundTag and isinstance(path_key, str)) or (
                    last_cls is ListTag and isinstance(path_key, int)
                )

                path_l[i] = (path_key, nbt_cls)
                last_cls = nbt_cls
            self._path = tuple[NBTPathElement, ...](path_l)

        assert isinstance(key, (str, int))
        if self._path is not None:
            if last_cls is CompoundTag:
                assert isinstance(key, str)
            elif last_cls is ListTag:
                assert isinstance(key, int)
        self._key = key

        assert isinstance(value, NBTTagClasses)
        self._snbt = value.to_snbt()
        self._value = value

    def __reduce__(self) -> Any:
        return NewNBTItem, (
            self._key,
            self._value,
            self._outer_name,
            self._outer_type,
            self._path,
        )

    def _data(self) -> Data:
        return (
            self._outer_name,
            self._outer_type,
            self._path,
            self._key,
            self._snbt,
        )

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)

        key = data["key"]
        assert isinstance(key, str | int)
        raw_value = data["value"]
        assert isinstance(raw_value, str)
        outer_name = data.get("outer_name", "")
        assert isinstance(outer_name, str)
        outer_type = data.get("outer_type", "compound")
        assert isinstance(outer_type, str)
        raw_path = data.get("path", None)
        if raw_path is None:
            path = None
        else:
            assert isinstance(raw_path, list)
            path = []
            for item in raw_path:
                assert isinstance(item, list) and len(item) == 2
                cls_key, cls_name = item
                assert isinstance(cls_key, str | int)
                assert isinstance(cls_name, str)
                path.append((cls_key, StrToNBTCls[cls_name]))

        return cls(
            key,
            read_snbt(raw_value),
            outer_name,
            StrToNBTCls[outer_type],
            path,
        )

    def to_json(self) -> JSONDict:
        options: JSONDict = {}
        if self._outer_name:
            options["outer_name"] = self._outer_name
        if self._outer_type is not CompoundTag:
            options["outer_type"] = NBTClsToStr[self._outer_type]
        if self._path is not None:
            options["path"] = [[key, NBTClsToStr[value]] for key, value in self._path]
        options["key"] = self._key
        options["value"] = self._value.to_snbt()
        return options

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        path: NBTPath
        if self._path is None:
            walked_path = state.nbt_path
            if walked_path is None:
                # If not used within walk_input_nbt then default to the root
                path = ()
            else:
                # If used within walk_input_nbt default to
                path = walked_path[2]
        else:
            # If path is defined then use that
            path = self._path

        dst.nbt.append(
            (self._outer_name, self._outer_type, path, self._key, self._value)
        )


class NewNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_nbt"
    _instances = {}

    # Instance variables
    _new_nbt: tuple[NewNBTItem, ...]

    def __init__(self, *new_nbt: NewNBTItem) -> None:
        super().__init__()
        self._new_nbt = tuple(new_nbt)
        if not all(isinstance(nbt, NewNBTItem) for nbt in self._new_nbt):
            raise TypeError

    def __reduce__(self) -> Any:
        return NewNBT, (*self._new_nbt,)

    def _data(self) -> Data:
        return self._new_nbt

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "new_nbt"
        options = data["options"]
        assert isinstance(options, list)
        return cls(*(NewNBTItem.from_json(opt) for opt in options))

    def to_json(self) -> JSONDict:
        return {
            "function": "new_nbt",
            "options": [opt.to_json() for opt in self._new_nbt],
        }

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        for item in self._new_nbt:
            item.run(src, state, dst)
