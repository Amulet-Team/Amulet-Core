from collections.abc import Mapping, Sequence
from typing import Any, Self, TypeVar

from _typeshed import Incomplete
from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict
from amulet_nbt import CompoundTag, ListTag

from ._frozen import FrozenMapping as FrozenMapping
from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from ._typing import NBTClsToStr as NBTClsToStr
from ._typing import NBTPath as NBTPath
from ._typing import NBTPathElement as NBTPathElement
from ._typing import NBTTagClsT as NBTTagClsT
from ._typing import StrToNBTCls as StrToNBTCls
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data
from .abc import follow_nbt_path as follow_nbt_path
from .abc import translation_function_from_json as translation_function_from_json

log: Incomplete
NBTLookUp: Incomplete
KeyT = TypeVar("KeyT", str, int)

class WalkInputNBTOptions(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self,
        nbt_cls: type[CompoundTag] | type[ListTag],
        self_default: AbstractBaseTranslationFunction | None = None,
        functions: AbstractBaseTranslationFunction | None = None,
        keys: Mapping[str, WalkInputNBTOptions] | None = None,
        index: Mapping[int, WalkInputNBTOptions] | None = None,
        nested_default: AbstractBaseTranslationFunction | None = None,
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...

class WalkInputNBT(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self,
        walk_nbt: WalkInputNBTOptions,
        path: Sequence[NBTPathElement] | None = None,
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
