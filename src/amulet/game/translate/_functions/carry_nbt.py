from __future__ import annotations

from typing import Self, Any

from amulet_nbt import CompoundTag, ListTag, AbstractBaseNumericTag

from .abc import (
    AbstractBaseTranslationFunction,
    Data,
    follow_nbt_path,
)
from amulet.game.abc import JSONCompatible, JSONDict
from ._typing import NBTTagClsT, NBTClsToStr, StrToNBTCls, NBTPath
from ._state import SrcData, StateData, DstData


class CarryNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "carry_nbt"
    _instances = {}

    # Instance variables
    _outer_name: str
    _outer_type: type[CompoundTag] | type[ListTag]
    _path: NBTPath | None
    _key: str | int | None
    _tag_cls: NBTTagClsT | None

    def __init__(
        self,
        outer_name: str = "",
        outer_type: type[CompoundTag] | type[ListTag] = CompoundTag,
        path: NBTPath | None = None,
        key: str | int | None = None,
        tag_cls: NBTTagClsT | None = None,
    ) -> None:
        super().__init__()
        self._outer_name = outer_name
        self._outer_type = outer_type
        self._path = path
        self._key = key
        self._tag_cls = tag_cls

    def __reduce__(self) -> Any:
        return CarryNBT, (
            self._outer_name,
            self._outer_type,
            self._path,
            self._key,
            self._tag_cls,
        )

    def _data(self) -> Data:
        return (
            self._outer_name,
            self._outer_type,
            self._path,
            self._key,
            self._tag_cls,
        )

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "carry_nbt"
        options = data.get("options", {})
        assert isinstance(options, dict)
        outer_name = options.get("outer_name", "")
        assert isinstance(outer_name, str)
        outer_type_name = options.get("outer_type", "compound")
        outer_type: type[CompoundTag] | type[ListTag]
        if outer_type_name == "compound":
            outer_type = CompoundTag
        elif outer_type_name == "list":
            outer_type = ListTag
        else:
            raise RuntimeError
        assert isinstance(outer_type_name, str)
        path: NBTPath | None
        if "path" in options:
            raw_path = options["path"]
            assert isinstance(raw_path, list)
            path_ = []
            for item in raw_path:
                assert isinstance(item, list) and len(item) == 2
                key, cls_name = item
                assert isinstance(key, str | int)
                nbt_cls: type[CompoundTag] | type[ListTag]
                if cls_name == "compound":
                    nbt_cls = CompoundTag
                elif cls_name == "list":
                    nbt_cls = ListTag
                else:
                    raise RuntimeError
                path_.append((key, nbt_cls))
            path = NBTPath(path_)
        else:
            path = None
        key = options.get("key", None)
        if key is not None:
            assert isinstance(key, str | int)
        cls_name = options.get("type", None)
        if cls_name is None:
            nbt_type = None
        else:
            assert isinstance(cls_name, str)
            nbt_type = StrToNBTCls[cls_name]

        return cls(
            outer_name,
            outer_type,
            path,
            key,
            nbt_type,
        )

    def to_json(self) -> JSONDict:
        options: JSONDict = {}
        if self._outer_name:
            options["outer_name"] = self._outer_name
        if self._outer_type is not CompoundTag:
            options["outer_type"] = NBTClsToStr[self._outer_type]
        if self._path is not None:
            options["path"] = [[key, NBTClsToStr[cls]] for key, cls in self._path]
        if self._key is not None:
            options["key"] = self._key
        if self._tag_cls is not None:
            options["type"] = NBTClsToStr[self._tag_cls]

        return {"function": "carry_nbt", "options": options}

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.cacheable = False

        src_nbt = src.nbt
        if src_nbt is None:
            return

        full_nbt_path = state.nbt_path
        if full_nbt_path is None:
            # This only works within walk_input_nbt
            return

        tag = follow_nbt_path(src_nbt, full_nbt_path)
        if tag is None:
            # Could not find the tag
            return

        nbt_path = full_nbt_path[2]
        path = nbt_path[:-1] if self._path is None else self._path
        src_key, src_cls = nbt_path[-1]
        key = src_key if self._key is None else self._key
        tag_cls = src_cls if self._tag_cls is None else self._tag_cls

        if not isinstance(tag, tag_cls):
            assert isinstance(tag, AbstractBaseNumericTag) and issubclass(
                tag_cls, AbstractBaseNumericTag
            )
            tag = tag_cls(tag)
        dst.nbt.append((self._outer_name, self._outer_type, path, key, tag))
