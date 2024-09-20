from typing import Any, Self, Sequence

from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict
from amulet_nbt import CompoundTag, ListTag

from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from ._typing import NBTClsToStr as NBTClsToStr
from ._typing import NBTPath as NBTPath
from ._typing import NBTPathElement as NBTPathElement
from ._typing import NBTTagClasses as NBTTagClasses
from ._typing import NBTTagT as NBTTagT
from ._typing import StrToNBTCls as StrToNBTCls
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data

class NewNBTItem(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self,
        key: str | int,
        value: NBTTagT,
        outer_name: str,
        outer_type: type[CompoundTag] | type[ListTag] = ...,
        path: (
            Sequence[tuple[str | int, type[CompoundTag] | type[ListTag]]] | None
        ) = None,
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...

class NewNBT(AbstractBaseTranslationFunction):
    Name: str
    def __init__(self, *new_nbt: NewNBTItem) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
