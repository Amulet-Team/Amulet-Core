from typing import Any, Self

from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONDict as JSONDict
from amulet_nbt import CompoundTag, ListTag

from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from ._typing import NBTClsToStr as NBTClsToStr
from ._typing import NBTPath as NBTPath
from ._typing import NBTTagClsT as NBTTagClsT
from ._typing import StrToNBTCls as StrToNBTCls
from .abc import AbstractBaseTranslationFunction as AbstractBaseTranslationFunction
from .abc import Data as Data
from .abc import follow_nbt_path as follow_nbt_path

class CarryNBT(AbstractBaseTranslationFunction):
    Name: str
    def __init__(
        self,
        outer_name: str,
        outer_type: type[CompoundTag] | type[ListTag] = ...,
        path: NBTPath | None = None,
        key: str | int | None = None,
        tag_cls: NBTTagClsT | None = None,
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None: ...
