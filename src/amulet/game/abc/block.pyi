import abc
from abc import ABC, abstractmethod
from collections.abc import Collection, Mapping
from typing import Callable, TypeVar

from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.data_types import BlockCoordinates as BlockCoordinates
from amulet.entity import Entity as Entity
from amulet.game import get_game_version as get_game_version
from amulet.game.translate import (
    BlockFromUniversalTranslator as BlockFromUniversalTranslator,
)
from amulet.game.translate import (
    BlockToUniversalTranslator as BlockToUniversalTranslator,
)
from amulet.version import VersionNumber as VersionNumber

from ._block_specification import BlockSpec as BlockSpec
from .game_version_container import GameVersionContainer as GameVersionContainer
from .version import GameVersion as GameVersion

T = TypeVar("T")

class BlockTranslationError(Exception):
    """An exception raised if the block could not be translated."""

class BlockData(GameVersionContainer, ABC, metaclass=abc.ABCMeta):
    def __init__(
        self,
        game_version: GameVersion,
        specification: Mapping[str, Mapping[str, BlockSpec]],
    ) -> None: ...
    def namespaces(self) -> Collection[str]:
        """An iterable of all the valid block namespaces."""

    def base_names(self, namespace: str) -> Collection[str]:
        """An iterable of all valid base names for the given namespace."""

    def get_specification(self, namespace: str, base_name: str) -> BlockSpec: ...
    def translate(
        self,
        target_platform: str,
        target_version: VersionNumber,
        block: Block,
        block_entity: BlockEntity | None = None,
        extra: (
            tuple[
                BlockCoordinates,
                Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
            ]
            | None
        ) = None,
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        """Translate a block from this version to the target version specified.

        :param target_platform: The game platform to convert to.
        :param target_version: The game version number to convert to.
        :param block: The block to translate
        :param block_entity: An optional block entity related to the block input
        :param extra: An optional tuple containing the absolute coordinate of the block in the world and a callback
            function taking a relative coordinate and returning the block and block entity at that coordinate.
            This is required for cases where the neighbour block is required to fully define the state.
            If the bool in the output is True this is required to fully define the translation.
        :return: There are two formats that can be returned.
            The first is a Block, optional BlockEntity and a bool.
            The second is an Entity, None and a bool.
            The bool specifies if block_location and get_block_callback are required to fully define the output data.
        :raises:
            ValueError: The arguments are incorrect. You did something wrong.
            BlockTranslationError: The translator is not aware of the block. You should handle a sensible default.
        """

    @abstractmethod
    def to_universal(
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
    ) -> tuple[Block, BlockEntity | None, bool]:
        """Convert a block to the universal format.

        This method should be considered private.

        :meta private:
        :param block: The block to translate
        :param block_entity: An optional block entity related to the block input
        :param extra: An optional tuple containing the absolute coordinate of the block in the world and a callback
            function taking a relative coordinate and returning the block and block entity at that coordinate.
            This is required for cases where the neighbour block is required to fully define the state.
            If the bool in the output is True this is required to fully define the translation.
        :return: A Block, optional BlockEntity and a bool.
            If the bool is True, the extra parameter is required to fully define the output data.
        :raises:
            ValueError: The arguments are incorrect. You did something wrong.
            BlockTranslationError: The translator is not aware of the block. You should handle a sensible default.
        """

    @abstractmethod
    def from_universal(
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
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        """Convert a block from the universal format.

        This method should be considered private.

        :meta private:
        :param target_platform: The game platform to convert to.
        :param target_version: The game version number to convert to.
        :param block: The block to translate
        :param block_entity: An optional block entity related to the block input
        :param extra: An optional tuple containing the absolute coordinate of the block in the world and a callback
            function taking a relative coordinate and returning the block and block entity at that coordinate.
            This is required for cases where the neighbour block is required to fully define the state.
            If the bool in the output is True this is required to fully define the translation.
        :return: There are two formats that can be returned.
            Block, optional BlockEntity and a bool.
            Entity, None and a bool.
            If the bool is True, the extra parameter is required to fully define the output data.
        :raises:
            ValueError: The arguments are incorrect. You did something wrong.
            BlockTranslationError: The translator is not aware of the block. You should handle a sensible default.
        """

class DatabaseBlockData(BlockData, ABC):
    def __init__(
        self,
        game_version: GameVersion,
        specification: Mapping[str, Mapping[str, BlockSpec]],
        to_universal: Mapping[tuple[str, str], BlockToUniversalTranslator],
        from_universal: Mapping[tuple[str, str], BlockFromUniversalTranslator],
    ) -> None: ...
    def to_universal(
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
    ) -> tuple[Block, BlockEntity | None, bool]: ...
    def from_universal(
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
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]: ...

class BlockDataNumericalComponent(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        """Convert the numerical id to its namespace id"""

    @abstractmethod
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int: ...
