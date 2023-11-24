from typing import Callable

from amulet.block import Block
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.api.data_types import BlockCoordinates

from .._block_specification import BlockSpec
from .._version import GameVersion
from ._functions import AbstractBaseTranslationFunction


# These classes exist to do some pre-translation and post-translation processing.
# They also store the constant data so that it doesn't need to be passed in each time.
# They don't do any caching


class BlockToUniversalTranslator:
    _instances =

    def __init__(
        self,
        spec: BlockSpec,
        translation: AbstractBaseTranslationFunction,
        universal_version: GameVersion,
    ):
        self._spec = spec
        self._translation = translation
        self._universal_version

    def run(
        self,
        block: Block,
        block_entity: BlockEntity | None,
        extra: tuple[BlockCoordinates, Callable[
            [BlockCoordinates], tuple[Block, BlockEntity | None]
        ]] | None
    ) -> tuple[Block, BlockEntity | None, bool, bool]:
        raise NotImplementedError


class BlockFromUniversalTranslator:
    def run(
        self,
        block: Block,
        block_entity: BlockEntity | None,
        extra: tuple[BlockCoordinates, Callable[
            [BlockCoordinates], tuple[Block, BlockEntity | None]
        ]] | None
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        raise NotImplementedError


class EntityToUniversalTranslator:
    def run(
        self,
        entity: Entity,
        extra: tuple[BlockCoordinates, Callable[
            [BlockCoordinates], tuple[Block, BlockEntity | None]
        ]] | None
    ) -> tuple[Block, BlockEntity | None, bool, bool]:
        raise NotImplementedError


class EntityFromUniversalTranslator:
    def run(
        self,
        entity: Entity | None,
        extra: tuple[BlockCoordinates, Callable[
            [BlockCoordinates], tuple[Block, BlockEntity | None]
        ]] | None
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        raise NotImplementedError
