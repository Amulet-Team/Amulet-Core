from __future__ import annotations

from typing import Self, TypeVar, Any
from collections.abc import Mapping, Iterator, Hashable, Iterable

from amulet_nbt import (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    FloatTag,
    DoubleTag,
    StringTag,
)

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    immutable_from_snbt,
    from_json,
    Data,
)
from ._frozen import FrozenMapping


class MapNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_nbt"
    _instances: dict[MapNBT, MapNBT] = {}

    # Instance variables
    _cases: FrozenMapping[
        str,
        AbstractBaseTranslationFunction,
    ]
    _default: AbstractBaseTranslationFunction

    def __new__(
        cls,
        cases: Mapping[
            str,
            AbstractBaseTranslationFunction,
        ],
        default: AbstractBaseTranslationFunction,
    ) -> MapNBT:
        self = super().__new__(cls)
        self._cases = FrozenMapping[
            str,
            AbstractBaseTranslationFunction,
        ](cases)
        assert all(
            isinstance(
                key,
                str,
            )
            and isinstance(value, AbstractBaseTranslationFunction)
            for key, value in self._cases.items()
        )
        assert isinstance(default, AbstractBaseTranslationFunction)
        self._default = default
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._cases, self._default

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "map_nbt"
        options = data["options"]
        assert isinstance(options, dict)
        cases = options.get("cases", {})
        assert isinstance(cases, dict)
        default = options.get("default", [])
        assert isinstance(default, list)
        return cls(
            {key: from_json(value) for key, value in cases.items()},
            from_json(default),
        )

    def to_json(self) -> JSONDict:
        options: JSONDict = {}
        if self._cases:
            options["cases"] = {
                key: value.to_json() for key, value in self._cases.items()
            }
        if self._default:
            options["default"] = self._default.to_json()
        return {"function": "map_nbt", "options": options}

    def run(self, *args, **kwargs):
        pass
