from __future__ import annotations

from typing import (
    Union,
    Sequence,
    Optional,
    Self,
    Any,
)
from collections.abc import Mapping

from amulet_nbt import (
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    LongArrayTag,
)

from .abc import AbstractBaseTranslationFunction, JSONCompatible, JSONDict, NBTClsToStr, NBTTagClsT, NBTTagT, NBTTagClasses, from_json


class NewNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_nbt"
    _instances: dict[Self, Self] = {}

    # Instance variables
    _outer_name: str
    _outer_type: NBTTagClsT
    _path: Optional[tuple[tuple[Union[str, int], str], ...]]
    _key: Union[str, int]
    _value: NBTTagT

    def __new__(
        cls,
        outer_name: str,
        outer_type: NBTTagClsT,
        path: Optional[Sequence[tuple[Union[str, int], NBTTagClsT]]],
        key: Union[str, int],
        value: NBTTagT
    ) -> Self:
        self = super().__new__(cls)

        if not isinstance(outer_name, str):
            raise TypeError
        self._outer_name = outer_name

        if outer_type not in NBTClsToStr:
            raise ValueError
        self._outer_type = outer_type

        if path is not None:
            path = list(path)
            for i, (key, val) in enumerate(path):
                if val not in {CompoundTag, ListTag}: #, ByteArrayTag, IntArrayTag, LongArrayTag}:
                    raise ValueError

                if i:
                    last_cls = path[i-1][1]
                else:
                    last_cls = self._outer_type

                if isinstance(key, str):
                    if last_cls is not CompoundTag:
                        raise TypeError
                elif isinstance(key, int):
                    if last_cls not in {ListTag, ByteArrayTag, IntArrayTag, LongArrayTag}:
                        raise TypeError
                else:
                    raise TypeError

                path[i] = (key, val)
            path = tuple(path)
        self._path = path

        # TODO: validate this better
        if not isinstance(key, (str, int)):
            raise TypeError
        self._key = key

        if not isinstance(value, NBTTagClasses):
            raise TypeError
        self._value = value
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if data.get("function") != "new_nbt":
            raise ValueError("Incorrect function data given.")
        return cls({
            block_name: from_json(function) for block_name, function in data["options"].items()
        })

    def to_json(self) -> JSONDict:

    # return {
    #     "function": "map_block_name",
    #     "options": {
    #         block_name: func.to_json() for block_name, func in self._blocks.items()
    #     },
    # }

    def __hash__(self) -> int:
        return hash(self._blocks)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NewNBT):
            return NotImplemented
        return self._blocks == other._blocks

    def run(self, *args, **kwargs):
        pass
