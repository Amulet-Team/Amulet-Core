from __future__ import annotations
from typing import Callable, Union, Sequence, TypeVar, Type, Any, TYPE_CHECKING
import json
import glob
import os
from concurrent.futures import ThreadPoolExecutor

from amulet_nbt import (
    read_nbt,
    read_snbt,
    NamedTag,
    ListTag,
    CompoundTag,
    AnyNBT,
)

from amulet.block import Block
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.data_types import BlockCoordinates
from amulet.version import VersionNumber

from ._functions import (
    AbstractBaseTranslationFunction,
    SrcData,
    SrcDataExtra,
    StateData,
    DstData,
)
from ._functions.abc import translation_function_from_json
from ._functions._typing import NBTPath

if TYPE_CHECKING:
    from amulet.game.abc import GameVersion, BlockSpec


# These classes exist to do some pre-translation and post-translation processing.
# They also store the constant data so that it doesn't need to be passed in each time.
# They don't do any caching


def create_nbt(
    outer_name: str,
    outer_type: type[ListTag] | type[CompoundTag],
    nbt_list: Sequence[
        tuple[
            str,
            type[ListTag] | type[CompoundTag],
            NBTPath,
            Union[str, int],
            AnyNBT,
        ]
    ],
    default_template: str | None = None,
) -> NamedTag:
    nbt_object: AnyNBT
    if default_template is None:
        nbt_object = outer_type()
    else:
        nbt_object = read_snbt(default_template)

    for nbt_entry in nbt_list:
        (
            element_outer_name,
            element_outer_type,
            element_nbt_path,
            element_data_path,
            element_data,
        ) = nbt_entry
        if outer_name == element_outer_name and issubclass(
            outer_type, element_outer_type
        ):
            nbt_temp: AnyNBT = nbt_object
            for path, nbt_type in element_nbt_path:
                # if the nested NBT object does not exist then create it
                if isinstance(nbt_temp, CompoundTag):
                    assert isinstance(path, str)
                    if path not in nbt_temp or not isinstance(nbt_temp[path], nbt_type):
                        nbt_temp[path] = nbt_type()
                    nbt_temp = nbt_temp[path]
                elif isinstance(nbt_temp, ListTag):
                    assert isinstance(path, int)
                    # if the list is a different type to nbt_type replace it with nbt_type
                    if len(nbt_temp) > 0 and not isinstance(nbt_temp[0], nbt_type):
                        raise RuntimeError("ListTag elements are the wrong type")

                    for _ in range(path + 1 - len(nbt_temp)):
                        # pad out the list to the length of the index
                        nbt_temp.append(nbt_type())
                    # we now should have a ListTag of the same type as nbt_type and length as path
                    nbt_temp = nbt_temp[path]
                else:
                    raise RuntimeError

            if isinstance(nbt_temp, CompoundTag):
                assert isinstance(element_data_path, str)
                nbt_temp[element_data_path] = element_data

            elif isinstance(nbt_temp, ListTag):
                assert isinstance(element_data_path, int)
                # if the list is a different type to data replace it with type(data)
                if (
                    len(nbt_temp) > 0
                    and nbt_temp[0].list_data_type != element_data.tag_id
                ):
                    raise RuntimeError("ListTag elements are the wrong type")

                for _ in range(element_data_path + 1 - len(nbt_temp)):
                    # pad out the list to the length of the index
                    nbt_temp.append(element_data.__class__())
                # we now should have a ListTag of the same type as nbt_type and length as data_path
                nbt_temp[element_data_path] = element_data

            # TODO:
            # elif isinstance(nbt_temp, ByteArrayTag) and isinstance(data, ByteTag):
            # 	# pad to the length of data_path if less than the current length
            # 	# nbt_temp[data_path] = data.value
            # elif isinstance(nbt_temp, IntArrayTag) and isinstance(data, IntTag):
            # elif isinstance(nbt_temp, LongArrayTag) and isinstance(data, LongTag):

    return NamedTag(nbt_object, outer_name)


class BlockToUniversalTranslator:
    # Class variables
    _instances: dict[BlockToUniversalTranslator, BlockToUniversalTranslator] = {}

    # Instance variables
    _src_spec: BlockSpec
    _translation: AbstractBaseTranslationFunction
    _universal_version: GameVersion
    _hash: int | None

    def __new__(
        cls,
        src_spec: BlockSpec,
        translation: AbstractBaseTranslationFunction,
        universal_version: GameVersion,
    ) -> BlockToUniversalTranslator:
        self = super().__new__(cls)
        self._src_spec = src_spec
        self._translation = translation
        self._universal_version = universal_version
        self._hash = None
        return cls._instances.setdefault(self, self)

    def __reduce__(self) -> Any:
        return BlockToUniversalTranslator, (
            self._src_spec,
            self._translation,
            self._universal_version,
        )

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(
                (self._src_spec, self._translation, self._universal_version)
            )
        return self._hash

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
    ) -> tuple[Block, BlockEntity | None, bool, bool]:
        if extra is None:
            src_extra = None
        else:
            coords, get_block = extra
            src_extra = SrcDataExtra(coords, get_block)

        block_entity_nbt = None if block_entity is None else block_entity.nbt

        if self._src_spec.nbt is not None and block_entity_nbt is None:
            # There should be a block entity
            if src_extra is not None:
                # Load it from the level
                block_entity = src_extra.get_block_callback((0, 0, 0))[1]
                if block_entity is not None:
                    block_entity_nbt = block_entity.nbt
            if block_entity_nbt is None:
                # If it is still None then load it from the specification
                block_entity_nbt = read_nbt(self._src_spec.nbt.snbt)

        src = SrcData(block, block_entity_nbt, src_extra)
        state = StateData()
        dst = DstData()
        self._translation.run(src, state, dst)

        assert dst.cls is Block
        assert dst.resource_id is not None
        namespace, base_name = dst.resource_id

        dst_spec = self._universal_version.block.get_specification(namespace, base_name)
        properties = {k: v.default for k, v in dst_spec.properties.items()}
        properties.update(dst.properties)

        dst_block = Block(
            "universal", VersionNumber(1), namespace, base_name, properties
        )

        if dst_spec.nbt is None:
            dst_block_entity = None
        else:
            dst_block_entity = BlockEntity(
                "universal",
                VersionNumber(1),
                dst_spec.nbt.namespace,
                dst_spec.nbt.base_name,
                create_nbt(
                    "",
                    CompoundTag,
                    dst.nbt,
                    dst_spec.nbt.snbt,
                ),
            )

        return dst_block, dst_block_entity, dst.extra_needed, dst.cacheable


class BlockFromUniversalTranslator:
    # Class variables
    _instances: dict[BlockFromUniversalTranslator, BlockFromUniversalTranslator] = {}

    # Instance variables
    _src_spec: BlockSpec
    _translation: AbstractBaseTranslationFunction
    _target_version: GameVersion
    _hash: int | None

    def __new__(
        cls,
        src_spec: BlockSpec,
        translation: AbstractBaseTranslationFunction,
        target_version: GameVersion,
    ) -> BlockFromUniversalTranslator:
        self = super().__new__(cls)
        self._src_spec = src_spec
        self._translation = translation
        self._target_version = target_version
        self._hash = None
        return cls._instances.setdefault(self, self)

    def __reduce__(self) -> Any:
        return BlockFromUniversalTranslator, (
            self._src_spec,
            self._translation,
            self._target_version,
        )

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash((self._src_spec, self._translation, self._target_version))
        return self._hash

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
    ) -> tuple[Block, BlockEntity | None, bool, bool] | tuple[Entity, None, bool, bool]:
        if extra is None:
            src_extra = None
        else:
            coords, get_block = extra
            src_extra = SrcDataExtra(coords, get_block)

        block_entity_nbt = None if block_entity is None else block_entity.nbt

        if self._src_spec.nbt is not None and block_entity_nbt is None:
            # There should be a block entity
            if src_extra is not None:
                # Load it from the level
                block_entity = src_extra.get_block_callback((0, 0, 0))[1]
                if block_entity is not None:
                    block_entity_nbt = block_entity.nbt
            if block_entity_nbt is None:
                # If it is still None then load it from the specification
                block_entity_nbt = read_nbt(self._src_spec.nbt.snbt)

        src = SrcData(block, block_entity_nbt, src_extra)
        state = StateData()
        dst = DstData()
        self._translation.run(src, state, dst)

        if dst.cls is Block:
            assert dst.resource_id is not None
            namespace, base_name = dst.resource_id

            dst_spec = self._target_version.block.get_specification(
                namespace, base_name
            )
            properties = {k: v.default for k, v in dst_spec.properties.items()}
            properties.update(dst.properties)

            dst_block = Block(
                target_platform, target_version, namespace, base_name, properties
            )

            if dst_spec.nbt is None:
                dst_block_entity = None
            else:
                dst_block_entity = BlockEntity(
                    target_platform,
                    target_version,
                    dst_spec.nbt.namespace,
                    dst_spec.nbt.base_name,
                    create_nbt(
                        "",
                        CompoundTag,
                        dst.nbt,
                        dst_spec.nbt.snbt,
                    ),
                )

            return dst_block, dst_block_entity, dst.extra_needed, dst.cacheable

        elif dst.cls is Entity:
            assert dst.resource_id is not None
            namespace, base_name = dst.resource_id

            # dst_spec = self._target_version.block.get_specification(
            #     namespace, base_name
            # )

            dst_entity = Entity(
                target_platform,
                target_version,
                namespace,
                base_name,
                0.0,
                0.0,
                0.0,
                create_nbt(
                    "",
                    CompoundTag,
                    dst.nbt,
                    # dst_spec.nbt.snbt,
                ),
            )

            return dst_entity, None, dst.extra_needed, dst.cacheable

        else:
            raise RuntimeError


TranslationClsT = TypeVar(
    "TranslationClsT", BlockToUniversalTranslator, BlockFromUniversalTranslator
)


def _read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def load_json_block_translations(
    version_path: str,
    block_format: str,
    direction: str,
    translation_cls: Type[TranslationClsT],
    get_src_spec: Callable[[str, str], BlockSpec],
    target_version: GameVersion,
) -> dict[tuple[str, str], TranslationClsT]:
    translations = dict[tuple[str, str], TranslationClsT]()
    paths = glob.glob(
        os.path.join(
            glob.escape(version_path),
            "block",
            block_format,
            direction,
            "*",
            "*",
            "*.json",
        )
    )
    with ThreadPoolExecutor() as e:
        for file_path, data in zip(paths, e.map(_read_file, paths)):
            *_, namespace, _, base_name = os.path.splitext(os.path.normpath(file_path))[
                0
            ].split(os.sep)
            translations[(namespace, base_name)] = translation_cls(
                get_src_spec(namespace, base_name),
                translation_function_from_json(json.loads(data)),
                target_version,
            )
    return translations


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
    ) -> tuple[Block, BlockEntity | None, bool, bool]:
        raise NotImplementedError


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
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        raise NotImplementedError
