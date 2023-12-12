from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING, TypeVar
from collections.abc import Mapping, Collection
from copy import deepcopy

from amulet.block import Block
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.api.data_types import BlockCoordinates
from amulet.version import VersionNumber
from amulet.game import get_game_version

from ._block_specification import BlockSpec

T = TypeVar("T")

if TYPE_CHECKING:
    from ._version import GameVersion
    from .translate import BlockToUniversalTranslator, BlockFromUniversalTranslator

    def proxy(obj: T) -> T:
        ...

else:
    from weakref import proxy


class TranslationError(Exception):
    """An exception raised if the block could not be translated."""


class BlockData(ABC):
    def __init__(
        self,
        game_version: GameVersion,
        specification: Mapping[str, Mapping[str, BlockSpec]],
    ) -> None:
        self._game_version = proxy(game_version)
        self._spec = specification

    def namespaces(self) -> Collection[str]:
        """An iterable of all the valid block namespaces."""
        return self._spec.keys()

    def base_names(self, namespace: str) -> Collection[str]:
        """An iterable of all valid base names for the given namespace."""
        return self._spec[namespace].keys()

    def get_specification(self, namespace: str, base_name: str) -> BlockSpec:
        return self._spec[namespace][base_name]

    @abstractmethod
    def translate(
        self,
        target_platform: str,
        target_version: VersionNumber,
        block: Block,
        block_entity: BlockEntity | None = None,
        extra: tuple[
            BlockCoordinates,
            Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
        ]
        | None = None,
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        """
        Translate a block from this version to the output version specified.

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
        """
        target_game_version = get_game_version(target_platform, target_version)
        universal_block, universal_block_entity, extra_needed = self.to_universal(
            block, block_entity, extra
        )
        (
            target_obj,
            target_block_entity,
            extra_needed2,
        ) = target_game_version.block.from_universal(
            target_platform,
            target_version,
            universal_block,
            universal_block_entity,
            extra,
        )
        if isinstance(target_obj, Block):
            return target_obj, target_block_entity, extra_needed or extra_needed2
        elif isinstance(target_obj, Entity):
            return target_obj, None, extra_needed or extra_needed2
        else:
            raise RuntimeError

    @abstractmethod
    def to_universal(
        self,
        block: Block,
        block_entity: BlockEntity | None,
        extra: tuple[
            BlockCoordinates,
            Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
        ]
        | None,
    ) -> tuple[Block, BlockEntity | None, bool]:
        """
        Convert a block to the universal format.
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
            ValueError: If the block is not compatible with this version.
            TranslationError: If the block does not exist in this version.
        """
        raise NotImplementedError

    @abstractmethod
    def from_universal(
        self,
        target_platform: str,
        target_version: VersionNumber,
        block: Block,
        block_entity: BlockEntity | None,
        extra: tuple[
            BlockCoordinates,
            Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
        ]
        | None,
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        """
        Convert a block to the universal format.
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
        """
        raise NotImplementedError


class DatabaseBlockData(BlockData):
    def __init__(
        self,
        game_version: GameVersion,
        specification: Mapping[str, Mapping[str, BlockSpec]],
        to_universal: Mapping[tuple[str, str], BlockToUniversalTranslator],
        from_universal: Mapping[tuple[str, str], BlockFromUniversalTranslator],
    ) -> None:
        super().__init__(game_version, specification)
        self._to_universal = to_universal
        self._from_universal = from_universal
        # Cache computed results so we don't need to recompute unnecessarily.
        self._to_universal_cache: dict[
            Block, tuple[Block, BlockEntity | None, bool]
        ] = {}
        self._from_universal_cache: dict[
            Block, tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]
        ] = {}

    def to_universal(
        self,
        block: Block,
        block_entity: BlockEntity | None,
        extra: tuple[
            BlockCoordinates,
            Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
        ]
        | None,
    ) -> tuple[Block, BlockEntity | None, bool]:
        if not self._game_version.supports_version(block.platform, block.version):
            raise ValueError("The block is not compatible with this version")

        if block_entity is None:
            if block in self._to_universal_cache:
                output, extra_output, extra_needed = self._to_universal_cache[block]
                return output, deepcopy(extra_output), extra_needed
        else:
            block_entity = deepcopy(block_entity)

        try:
            translator = self._to_universal[(block.namespace, block.base_name)]
        except KeyError:
            raise TranslationError(
                f"Block {block} does not exist in version {self._game_version.platform} {self._game_version.min_version}"
            )

        output, extra_output, extra_needed, cacheable = translator.run(
            block, block_entity, extra
        )

        if cacheable:
            self._to_universal_cache[block] = output, extra_output, extra_needed

        return output, deepcopy(extra_output), extra_needed

    def from_universal(
        self,
        target_platform: str,
        target_version: VersionNumber,
        block: Block,
        block_entity: BlockEntity | None,
        extra: tuple[
            BlockCoordinates,
            Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
        ]
        | None,
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        if not self._game_version.supports_version(target_platform, target_version):
            raise ValueError("The target version is not compatible with this version")

        if block.platform != "universal":
            raise ValueError("The source block is not in the universal format")

        if block_entity is None:
            if block in self._from_universal_cache:
                output, extra_output, extra_needed = self._from_universal_cache[block]
                if isinstance(output, Block):
                    return output, deepcopy(extra_output), extra_needed
                elif isinstance(output, Entity):
                    return deepcopy(output), None, extra_needed
        else:
            block_entity = deepcopy(block_entity)

        try:
            translator = self._from_universal[(block.namespace, block.base_name)]
        except KeyError:
            raise TranslationError(
                f"Block {block} does not exist in version {self._game_version.platform} {self._game_version.min_version}"
            )

        output, extra_output, extra_needed, cacheable = translator.run(
            target_platform, target_version, block, block_entity, extra
        )

        if isinstance(output, Block):
            if cacheable:
                self._from_universal_cache[block] = (
                    output,
                    deepcopy(extra_output),
                    extra_needed,
                )
            return output, deepcopy(extra_output), extra_needed
        elif isinstance(output, Entity):
            if cacheable:
                self._from_universal_cache[block] = deepcopy(output), None, extra_needed
            return deepcopy(output), None, extra_needed


class BlockDataNumericalComponent(ABC):
    @abstractmethod
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        """Convert the numerical id to its namespace id"""
        raise NotImplementedError

    @abstractmethod
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        raise NotImplementedError
