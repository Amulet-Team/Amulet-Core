from typing import Any, Callable, Sequence, TypeVar

from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.data_types import BlockCoordinates as BlockCoordinates
from amulet.entity import Entity as Entity
from amulet.game.abc import BlockSpec as BlockSpec
from amulet.game.abc import GameVersion as GameVersion
from amulet.version import VersionNumber as VersionNumber
from amulet_nbt import AnyNBT as AnyNBT
from amulet_nbt import CompoundTag, ListTag, NamedTag

from ._functions import (
    AbstractBaseTranslationFunction as AbstractBaseTranslationFunction,
)
from ._functions import DstData as DstData
from ._functions import SrcData as SrcData
from ._functions import SrcDataExtra as SrcDataExtra
from ._functions import StateData as StateData
from ._functions._typing import NBTPath as NBTPath
from ._functions.abc import (
    translation_function_from_json as translation_function_from_json,
)

def create_nbt(
    outer_name: str,
    outer_type: type[ListTag] | type[CompoundTag],
    nbt_list: Sequence[
        tuple[str, type[ListTag] | type[CompoundTag], NBTPath, str | int, AnyNBT]
    ],
    default_template: str | None = None,
) -> NamedTag: ...

class BlockToUniversalTranslator:
    def __new__(
        cls,
        src_spec: BlockSpec,
        translation: AbstractBaseTranslationFunction,
        universal_version: GameVersion,
    ) -> BlockToUniversalTranslator: ...
    def __reduce__(self) -> Any: ...
    def __hash__(self) -> int: ...
    def run(
        self,
        block: Block,
        block_entity: BlockEntity | None,
        extra: (
            tuple[
                BlockCoordinates,
                Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
            ]
            | None
        ),
    ) -> tuple[Block, BlockEntity | None, bool, bool]: ...

class BlockFromUniversalTranslator:
    def __new__(
        cls,
        src_spec: BlockSpec,
        translation: AbstractBaseTranslationFunction,
        target_version: GameVersion,
    ) -> BlockFromUniversalTranslator: ...
    def __reduce__(self) -> Any: ...
    def __hash__(self) -> int: ...
    def run(
        self,
        target_platform: str,
        target_version: VersionNumber,
        block: Block,
        block_entity: BlockEntity | None,
        extra: (
            tuple[
                BlockCoordinates,
                Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
            ]
            | None
        ),
    ) -> (
        tuple[Block, BlockEntity | None, bool, bool] | tuple[Entity, None, bool, bool]
    ): ...

TranslationClsT = TypeVar(
    "TranslationClsT", BlockToUniversalTranslator, BlockFromUniversalTranslator
)

def load_json_block_translations(
    version_path: str,
    block_format: str,
    direction: str,
    translation_cls: type[TranslationClsT],
    get_src_spec: Callable[[str, str], BlockSpec],
    target_version: GameVersion,
) -> dict[tuple[str, str], TranslationClsT]: ...

class EntityToUniversalTranslator:
    def run(
        self,
        entity: Entity,
        extra: (
            tuple[
                BlockCoordinates,
                Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
            ]
            | None
        ),
    ) -> tuple[Block, BlockEntity | None, bool, bool]: ...

class EntityFromUniversalTranslator:
    def run(
        self,
        entity: Entity | None,
        extra: (
            tuple[
                BlockCoordinates,
                Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
            ]
            | None
        ),
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]: ...
