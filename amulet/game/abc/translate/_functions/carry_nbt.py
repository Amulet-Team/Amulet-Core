from __future__ import annotations

from typing import Self
from collections.abc import Sequence

from amulet_nbt import CompoundTag

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    NBTTagClsT,
    NBTClsToStr,
    StrToNBTCls,
    Data,
)


class CarryNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "carry_nbt"
    _instances: dict[CarryNBT, CarryNBT] = {}

    # Instance variables
    _outer_name: str
    _outer_type: NBTTagClsT
    _path: tuple[tuple[str | int, NBTTagClsT], ...] | None
    _key: str | int | None
    _tag_cls: NBTTagClsT | None

    def __new__(
        cls,
        outer_name: str = "",
        outer_type: NBTTagClsT = CompoundTag,
        path: Sequence[tuple[str | int, NBTTagClsT]] | None = None,
        key: str | int | None = None,
        tag_cls: NBTTagClsT | None = None,
    ) -> CarryNBT:
        self = super().__new__(cls)
        self._outer_name = outer_name
        self._outer_type = outer_type
        self._path = (
            None if path is None else tuple[tuple[str | int, NBTTagClsT], ...](path)
        )
        self._key = key
        self._tag_cls = tag_cls
        return cls._instances.setdefault(self, self)

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
        assert isinstance(outer_type_name, str)
        path: list[tuple[str | int, NBTTagClsT]] | None
        if "path" in options:
            raw_path = options["path"]
            assert isinstance(raw_path, list)
            path = []
            for item in raw_path:
                assert isinstance(item, tuple) and len(item) == 2
                key, cls_name = item
                assert isinstance(key, str | int)
                assert isinstance(cls_name, str)
                path.append((key, StrToNBTCls[cls_name]))
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
            StrToNBTCls[outer_type_name],
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

    def run(self, *args, **kwargs):
        pass
