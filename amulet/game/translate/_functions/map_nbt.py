from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping

from .abc import (
    AbstractBaseTranslationFunction,
    translation_function_from_json,
    Data,
    follow_nbt_path,
)
from amulet.game.abc import JSONCompatible, JSONDict
from ._frozen import FrozenMapping
from ._state import SrcData, StateData, DstData


class MapNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_nbt"
    _instances = {}

    # Instance variables
    _cases: FrozenMapping[
        str,
        AbstractBaseTranslationFunction,
    ]
    _default: AbstractBaseTranslationFunction | None

    def __init__(
        self,
        cases: Mapping[
            str,
            AbstractBaseTranslationFunction,
        ],
        default: AbstractBaseTranslationFunction | None,
    ) -> None:
        super().__init__()
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
        assert default is None or isinstance(default, AbstractBaseTranslationFunction)
        self._default = default

    def __reduce__(self) -> Any:
        return MapNBT, (self._cases, self._default)

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
        raw_default = options.get("default", None)
        if raw_default is None:
            default = None
        else:
            assert isinstance(raw_default, list)
            default = translation_function_from_json(raw_default)
        return cls(
            {
                key: translation_function_from_json(value)
                for key, value in cases.items()
            },
            default,
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

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.cacheable = False
        if src.nbt is None:
            dst.extra_needed = True
            return

        if state.nbt_path is None:
            return

        run_default = True

        if self._cases:
            nbt = follow_nbt_path(src.nbt, state.nbt_path)
            if nbt is not None:
                nbt_hash = nbt.to_snbt()
                if nbt_hash in self._cases:
                    self._cases[nbt_hash].run(src, state, dst)
                    run_default = False

        if run_default and self._default is not None:
            self._default.run(src, state, dst)
