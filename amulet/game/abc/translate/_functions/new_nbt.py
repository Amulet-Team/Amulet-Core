from __future__ import annotations

from typing import (
    Sequence,
    Self,
)

from amulet_nbt import (
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    LongArrayTag,
    from_snbt,
)

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    NBTClsToStr,
    NBTTagClsT,
    NBTTagT,
    NBTTagClasses,
    Data,
    StrToNBTCls,
)


class NewNBTItem(AbstractBaseTranslationFunction):
    # Class variables
    Name = "_new_nbt"
    _instances: dict[NewNBTItem, NewNBTItem] = {}

    # Instance variables
    _key: str | int
    _value: NBTTagT
    _snbt: str
    _outer_name: str
    _outer_type: type[CompoundTag] | type[ListTag]
    _path: tuple[tuple[str | int, NBTTagClsT], ...] | None

    def __new__(
        cls,
        key: str | int,
        value: NBTTagT,
        outer_name: str = "",
        outer_type: type[CompoundTag] | type[ListTag] = CompoundTag,
        path: Sequence[tuple[str | int, NBTTagClsT]] | None = None,
    ) -> NewNBTItem:
        self = super().__new__(cls)
        assert isinstance(outer_name, str)
        self._outer_name = outer_name

        assert outer_type in NBTClsToStr
        self._outer_type = outer_type
        last_cls = outer_type

        if path is not None:
            path = list(path)
            for i, (path_key, nbt_cls) in enumerate(path):
                if nbt_cls not in {
                    CompoundTag,
                    ListTag,
                }:  # , ByteArrayTag, IntArrayTag, LongArrayTag}:
                    raise ValueError

                if isinstance(path_key, str):
                    if last_cls is not CompoundTag:
                        raise TypeError
                elif isinstance(path_key, int):
                    if last_cls not in {
                        ListTag,
                        ByteArrayTag,
                        IntArrayTag,
                        LongArrayTag,
                    }:
                        raise TypeError
                else:
                    raise TypeError

                path[i] = (path_key, nbt_cls)
                last_cls = path[i - 1][1]
            path = tuple[tuple[str | int, NBTTagClsT], ...](path)
        self._path = path

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
        return cls._instances.setdefault(self, self)

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
        assert isinstance(outer_name, str)
        raw_path = data.get("path", None)
        assert raw_path is None or isinstance(raw_path, list)
        path = (
            None
            if raw_path is None
            else tuple((key, StrToNBTCls[cls_name]) for key, cls_name in raw_path)
        )

        return cls(
            key,
            from_snbt(raw_value),
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

    def run(self, *args, **kwargs):
        pass


class NewNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_nbt"
    _instances: dict[NewNBT, NewNBT] = {}

    # Instance variables
    _new_nbt: tuple[NewNBTItem]

    def __new__(cls, *new_nbt: NewNBTItem) -> NewNBT:
        self = super().__new__(cls)
        self._new_nbt = tuple(new_nbt)
        if not all(isinstance(nbt, NewNBTItem) for nbt in self._new_nbt):
            raise TypeError
        return cls._instances.setdefault(self, self)

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

    def run(self, *args, **kwargs):
        pass
