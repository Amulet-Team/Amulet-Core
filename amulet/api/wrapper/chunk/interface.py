from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Tuple,
    Any,
    Union,
    TYPE_CHECKING,
    Optional,
    overload,
    Type,
    Sequence,
    Callable,
)
from enum import Enum

from amulet.api.block_entity import BlockEntity
from amulet.api.entity import Entity
from amulet.api.data_types import AnyNDArray, VersionNumberAny, VersionIdentifierType
from amulet_nbt import (
    AbstractBaseTag,
    ListTag,
    CompoundTag,
    AnyNBT,
    NamedTag,
    StringTag,
    IntTag,
    IntArrayTag,
    DoubleTag,
    FloatTag,
)

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from amulet.api.chunk import Chunk


class EntityIDType(Enum):
    int_id = 0
    str_id = 1
    namespace_str_id = 2
    namespace_str_Id = 3
    namespace_str_identifier = 4


class EntityCoordType(Enum):
    xyz_int = 0
    Pos_list_float = 1
    Pos_list_double = 2
    Pos_list_int = 3
    Pos_array_int = 4


PosTypeMap = {
    3: EntityCoordType.Pos_list_int,
    5: EntityCoordType.Pos_list_float,
    6: EntityCoordType.Pos_list_double,
}


class Interface(ABC):
    @abstractmethod
    def decode(self, *args, **kwargs) -> Tuple["Chunk", AnyNDArray]:
        raise NotImplementedError

    def _decode_entity(
        self,
        nbt: NamedTag,
        id_type: EntityIDType,
        coord_type: EntityCoordType,
    ) -> Optional[Entity]:
        entity = self._decode_base_entity(nbt, id_type, coord_type)
        if entity is not None:
            namespace, base_name, x, y, z, nbt = entity
            return Entity(
                namespace=namespace, base_name=base_name, x=x, y=y, z=z, nbt=nbt
            )

    def _decode_block_entity(
        self,
        nbt: NamedTag,
        id_type: EntityIDType,
        coord_type: EntityCoordType,
    ) -> Optional[BlockEntity]:
        entity = self._decode_base_entity(nbt, id_type, coord_type)
        if entity is not None:
            namespace, base_name, x, y, z, nbt = entity
            return BlockEntity(
                namespace=namespace, base_name=base_name, x=x, y=y, z=z, nbt=nbt
            )

    @staticmethod
    def _decode_base_entity(
        named_tag: NamedTag, id_type: EntityIDType, coord_type: EntityCoordType
    ) -> Optional[
        Tuple[
            str,
            str,
            Union[int, float],
            Union[int, float],
            Union[int, float],
            NamedTag,
        ]
    ]:
        if not (
            isinstance(named_tag, NamedTag) and isinstance(named_tag.tag, CompoundTag)
        ):
            return

        nbt_tag = named_tag.tag

        if id_type == EntityIDType.namespace_str_id:
            entity_id = nbt_tag.pop("id", StringTag(""))
            if (
                not isinstance(entity_id, StringTag)
                or entity_id.py_str == ""
                or ":" not in entity_id.py_str
            ):
                return
            namespace, base_name = entity_id.py_str.split(":", 1)

        elif id_type == EntityIDType.namespace_str_Id:
            entity_id = nbt_tag.pop("Id", StringTag(""))
            if (
                not isinstance(entity_id, StringTag)
                or entity_id.py_str == ""
                or ":" not in entity_id.py_str
            ):
                return
            namespace, base_name = entity_id.py_str.split(":", 1)

        elif id_type == EntityIDType.str_id:
            entity_id = nbt_tag.pop("id", StringTag(""))
            if not isinstance(entity_id, StringTag) or entity_id.py_str == "":
                return
            namespace = ""
            base_name = entity_id.py_str

        elif id_type in [EntityIDType.namespace_str_identifier, EntityIDType.int_id]:
            if "identifier" in nbt_tag:
                entity_id = nbt_tag.pop("identifier")
                if (
                    not isinstance(entity_id, StringTag)
                    or entity_id.py_str == ""
                    or ":" not in entity_id.py_str
                ):
                    return
                namespace, base_name = entity_id.py_str.split(":", 1)
            elif "id" in nbt_tag:
                entity_id = nbt_tag.pop("id")
                if not isinstance(entity_id, IntTag):
                    return
                namespace = ""
                base_name = str(entity_id.py_int)
            else:
                return
        else:
            raise NotImplementedError(f"Entity id type {id_type}")

        if coord_type in [
            EntityCoordType.Pos_list_double,
            EntityCoordType.Pos_list_float,
            EntityCoordType.Pos_list_int,
        ]:
            if "Pos" not in nbt_tag:
                return
            pos = nbt_tag.pop("Pos")
            pos: ListTag

            if (
                not isinstance(pos, ListTag)
                or len(pos) != 3
                or PosTypeMap.get(pos.list_data_type) != coord_type
            ):
                return
            x, y, z = [c.py_data for c in pos]
        elif coord_type == EntityCoordType.Pos_array_int:
            if "Pos" not in nbt_tag:
                return
            pos = nbt_tag.pop("Pos")
            pos: IntArrayTag

            if not isinstance(pos, IntArrayTag) or len(pos) != 3:
                return
            x, y, z = pos
        elif coord_type == EntityCoordType.xyz_int:
            if not all(
                c in nbt_tag and isinstance(nbt_tag[c], IntTag) for c in ("x", "y", "z")
            ):
                return
            x, y, z = [nbt_tag.pop(c).py_int for c in ("x", "y", "z")]
        else:
            raise NotImplementedError(f"Entity coord type {coord_type}")

        return namespace, base_name, x, y, z, named_tag

    @abstractmethod
    def encode(self, *args, **kwargs) -> Any:
        """
        Take a version-specific chunk and encode it to raw data for the format to store.
        """
        raise NotImplementedError

    def _encode_entity(
        self, entity: Entity, id_type: EntityIDType, coord_type: EntityCoordType
    ) -> Optional[NamedTag]:
        return self._encode_base_entity(entity, id_type, coord_type)

    def _encode_block_entity(
        self, entity: BlockEntity, id_type: EntityIDType, coord_type: EntityCoordType
    ) -> Optional[NamedTag]:
        return self._encode_base_entity(entity, id_type, coord_type)

    @staticmethod
    def _encode_base_entity(
        entity: Union[Entity, BlockEntity],
        id_type: EntityIDType,
        coord_type: EntityCoordType,
    ) -> Optional[NamedTag]:
        if not isinstance(entity.nbt, NamedTag) and isinstance(
            entity.nbt.tag, CompoundTag
        ):
            return
        named_tag = entity.nbt
        tag = named_tag.compound

        if id_type == EntityIDType.namespace_str_id:
            tag["id"] = StringTag(entity.namespaced_name)
        elif id_type == EntityIDType.namespace_str_Id:
            tag["Id"] = StringTag(entity.namespaced_name)
        elif id_type == EntityIDType.namespace_str_identifier:
            tag["identifier"] = StringTag(entity.namespaced_name)
        elif id_type == EntityIDType.str_id:
            tag["id"] = StringTag(entity.base_name)
        elif id_type == EntityIDType.int_id:
            if not entity.base_name.isnumeric():
                return
            tag["id"] = IntTag(int(entity.base_name))
        else:
            raise NotImplementedError(f"Entity id type {id_type}")

        if coord_type == EntityCoordType.Pos_list_double:
            tag["Pos"] = ListTag(
                [
                    DoubleTag(float(entity.x)),
                    DoubleTag(float(entity.y)),
                    DoubleTag(float(entity.z)),
                ]
            )
        elif coord_type == EntityCoordType.Pos_list_float:
            tag["Pos"] = ListTag(
                [
                    FloatTag(float(entity.x)),
                    FloatTag(float(entity.y)),
                    FloatTag(float(entity.z)),
                ]
            )
        elif coord_type == EntityCoordType.Pos_list_int:
            tag["Pos"] = ListTag(
                [
                    IntTag(int(entity.x)),
                    IntTag(int(entity.y)),
                    IntTag(int(entity.z)),
                ]
            )
        elif coord_type == EntityCoordType.Pos_array_int:
            tag["Pos"] = IntArrayTag([int(entity.x), int(entity.y), int(entity.z)])
        elif coord_type == EntityCoordType.xyz_int:
            tag["x"] = IntTag(int(entity.x))
            tag["y"] = IntTag(int(entity.y))
            tag["z"] = IntTag(int(entity.z))
        else:
            raise NotImplementedError(f"Entity coord type {coord_type}")

        return named_tag

    @overload
    @staticmethod
    def check_type(obj: CompoundTag, key: str, dtype: Type[AnyNBT]) -> bool:
        ...

    @overload
    @staticmethod
    def check_type(obj: ListTag, key: int, dtype: Type[AnyNBT]) -> bool:
        ...

    @staticmethod
    def check_type(
        obj: Union[CompoundTag, ListTag], key: Union[str, int], dtype: Type[AnyNBT]
    ) -> bool:
        """Check the key exists and the type is correct."""
        return key in obj and isinstance(obj[key], dtype)

    @overload
    def get_obj(
        self,
        obj: CompoundTag,
        key: str,
        dtype: Type[AnyNBT],
        default: Optional[AnyNBT] = None,
    ) -> Optional[AnyNBT]:
        ...

    @overload
    def get_obj(
        self,
        obj: ListTag,
        key: int,
        dtype: Type[AnyNBT],
        default: Optional[AnyNBT] = None,
    ) -> Optional[AnyNBT]:
        ...

    def get_obj(
        self, obj, key, dtype: Type[AnyNBT], default: Optional[AnyNBT] = None
    ) -> Optional[AnyNBT]:
        """Pop a key from a container object if it exists and the type is correct. Otherwise return default.
        This works in much the same way as dict.get but uses default if the data type does not match.

        :param obj: The CompoundTag to read from.
        :param key: The key to use.
        :param dtype: The expected data type.
        :param default: The default value to use if the existing is not valid. If None will use dtype()
        :return: The final value in the key.
        """
        if key in obj:
            if isinstance(obj[key], dtype):
                # if it exists and is correct
                return obj.pop(key)
        if default is None:
            return dtype()
        return default

    def get_nested_obj(
        self,
        obj: Union[CompoundTag, ListTag],
        path: Sequence[  # The path to the object.
            Tuple[Union[str, int], Type[AbstractBaseTag]],
        ],
        default: Union[None, AnyNBT, Callable[[], Any]] = None,
        *,
        pop_last=False,
    ):
        """
        Get an object from a nested NBT structure

        :param obj: The root NBT object
        :param path: The path to the desired object (key, dtype)
        :param default: The default value to use if the existing is not valid. If default is callable then return the called result.
        :param pop_last: If true the last key will be popped
        :return:
        """
        try:
            last_index = len(path) - 1
            for i, (key, dtype) in enumerate(path):
                if i == last_index and pop_last:
                    obj = obj.pop(key)
                else:
                    obj = obj[key]
                if dtype is not obj.__class__:
                    raise TypeError
        except (KeyError, IndexError, TypeError):
            if default is None or isinstance(default, AbstractBaseTag):
                return default
            elif callable(default):
                return default()
            else:
                raise TypeError(
                    "default must be None, an NBT instance or an NBT class."
                )
        else:
            return obj

    @staticmethod
    def set_obj(
        obj: CompoundTag,
        key: str,
        dtype: Type[AnyNBT],
        default: Union[None, AnyNBT, Callable[[], Any]] = None,
        path: Sequence[str] = (),  # The path to the object.
        *,
        setdefault=False,
    ) -> AnyNBT:
        """
        Works like setdefualt on a dictionary but works with an optional nested path.

        :param obj: The compound tag to get the data from
        :param key: The key to setdefault
        :param dtype: The dtype that the key must be
        :param default: The default value to set if it does not exist or the type is wrong
        :param path: Optional path to the nested compound.
        :param setdefault: If True will behave like setdefault. If False will replace existing data.
        :return: The data at the path
        """
        for path_key in path:
            obj_ = obj.get(path_key, None)
            if not isinstance(obj_, CompoundTag):
                # if it does not exist or the type is wrong then create it
                obj_ = obj[path_key] = CompoundTag()
            obj = obj_
        obj_ = obj.get(key, None)
        if not setdefault or not isinstance(obj_, dtype):
            # if it does not exist or the type is wrong then create it
            if default is None:
                obj_ = dtype()
            elif isinstance(default, AbstractBaseTag):
                obj_ = default
            elif callable(default):
                obj_ = default()
            else:
                raise TypeError(
                    "default must be None, an NBT instance or an NBT class."
                )
            obj[key] = obj_
        return obj_

    @abstractmethod
    def get_translator(
        self,
        max_world_version: VersionIdentifierType,
        data: Any = None,
    ) -> Tuple["Translator", VersionNumberAny]:
        """
        Get the Translator class for the requested version.
        :param max_world_version: The game version the world was last opened in. Version number tuple or data version number.
        :param data: Optional data to get translator based on chunk version rather than world version
        :return: Tuple[Translator, version number for PyMCTranslate to use]
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def is_valid(key: Tuple) -> bool:
        """
        Returns whether this Interface is able to interface with the chunk type with a given identifier key,
        generated by the format.

        :param key: The key who's decodability needs to be checked.
        :return: True if this interface can interface with the chunk version associated with the key, False otherwise.
        """
        raise NotImplementedError
