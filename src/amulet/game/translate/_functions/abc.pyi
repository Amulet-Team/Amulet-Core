from abc import ABCMeta, abstractmethod
from typing import Any, ClassVar, Protocol

from amulet.block import PropertyValueType as PropertyValueType
from amulet.game.abc import JSONCompatible as JSONCompatible
from amulet.game.abc import JSONInterface as JSONInterface
from amulet_nbt import CompoundTag, ListTag
from amulet_nbt import NamedTag as NamedTag

from ._state import DstData as DstData
from ._state import SrcData as SrcData
from ._state import StateData as StateData
from ._typing import NBTPath as NBTPath
from ._typing import NBTTagT as NBTTagT

def immutable_from_snbt(snbt: str) -> PropertyValueType: ...
def follow_nbt_path(
    nbt: NamedTag, nbt_path: tuple[str, type[CompoundTag] | type[ListTag], NBTPath]
) -> NBTTagT | None: ...
def translation_function_from_json(
    data: JSONCompatible,
) -> AbstractBaseTranslationFunction: ...

class Data(Protocol):
    def __hash__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...

class CacheMeta(ABCMeta):
    """This modifies the construction of the instance to always return a cached instance, if one exists."""

    def __call__(cls, *args: Any, **kwargs: Any) -> AbstractBaseTranslationFunction: ...

class AbstractBaseTranslationFunction(JSONInterface, metaclass=CacheMeta):
    Name: ClassVar[str]
    def __init__(self) -> None: ...
    def __init_subclass__(cls, **kwargs: Any) -> None: ...
    @abstractmethod
    def __reduce__(self) -> Any: ...
    def __bool__(self) -> bool: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
    @abstractmethod
    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        """Run the translation function"""
