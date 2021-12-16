from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Any, Union, TYPE_CHECKING, Optional, overload, Type
from enum import Enum

from amulet.api.block_entity import BlockEntity
from amulet.api.entity import Entity
from amulet.api.data_types import AnyNDArray, VersionNumberAny, VersionIdentifierType
import amulet_nbt
from amulet_nbt import TAG_List, TAG_Compound, AnyNBT

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
        nbt: amulet_nbt.NBTFile,
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
        nbt: amulet_nbt.NBTFile,
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
        nbt: amulet_nbt.NBTFile, id_type: EntityIDType, coord_type: EntityCoordType
    ) -> Optional[
        Tuple[
            str,
            str,
            Union[int, float],
            Union[int, float],
            Union[int, float],
            amulet_nbt.NBTFile,
        ]
    ]:
        if not (
            isinstance(nbt, amulet_nbt.NBTFile)
            and isinstance(nbt.value, amulet_nbt.TAG_Compound)
        ):
            return

        if id_type == EntityIDType.namespace_str_id:
            entity_id = nbt.pop("id", amulet_nbt.TAG_String(""))
            if (
                not isinstance(entity_id, amulet_nbt.TAG_String)
                or entity_id.value == ""
                or ":" not in entity_id.value
            ):
                return
            namespace, base_name = entity_id.value.split(":", 1)

        elif id_type == EntityIDType.namespace_str_Id:
            entity_id = nbt.pop("Id", amulet_nbt.TAG_String(""))
            if (
                not isinstance(entity_id, amulet_nbt.TAG_String)
                or entity_id.value == ""
                or ":" not in entity_id.value
            ):
                return
            namespace, base_name = entity_id.value.split(":", 1)

        elif id_type == EntityIDType.str_id:
            entity_id = nbt.pop("id", amulet_nbt.TAG_String(""))
            if (
                not isinstance(entity_id, amulet_nbt.TAG_String)
                or entity_id.value == ""
            ):
                return
            namespace = ""
            base_name = entity_id.value

        elif id_type in [EntityIDType.namespace_str_identifier, EntityIDType.int_id]:
            if "identifier" in nbt:
                entity_id = nbt.pop("identifier")
                if (
                    not isinstance(entity_id, amulet_nbt.TAG_String)
                    or entity_id.value == ""
                    or ":" not in entity_id.value
                ):
                    return
                namespace, base_name = entity_id.value.split(":", 1)
            elif "id" in nbt:
                entity_id = nbt.pop("id")
                if not isinstance(entity_id, amulet_nbt.TAG_Int):
                    return
                namespace = ""
                base_name = str(entity_id.value)
            else:
                return
        else:
            raise NotImplementedError(f"Entity id type {id_type}")

        if coord_type in [
            EntityCoordType.Pos_list_double,
            EntityCoordType.Pos_list_float,
            EntityCoordType.Pos_list_int,
        ]:
            if "Pos" not in nbt:
                return
            pos = nbt.pop("Pos")
            pos: amulet_nbt.TAG_List

            if (
                not isinstance(pos, amulet_nbt.TAG_List)
                or len(pos) != 3
                or PosTypeMap.get(pos.list_data_type) != coord_type
            ):
                return
            x, y, z = [c.value for c in pos]
        elif coord_type == EntityCoordType.Pos_array_int:
            if "Pos" not in nbt:
                return
            pos = nbt.pop("Pos")
            pos: amulet_nbt.TAG_Int_Array

            if not isinstance(pos, amulet_nbt.TAG_Int_Array) or len(pos) != 3:
                return
            x, y, z = pos
        elif coord_type == EntityCoordType.xyz_int:
            if not all(
                c in nbt and isinstance(nbt[c], amulet_nbt.TAG_Int)
                for c in ("x", "y", "z")
            ):
                return
            x, y, z = [nbt.pop(c).value for c in ("x", "y", "z")]
        else:
            raise NotImplementedError(f"Entity coord type {coord_type}")

        return namespace, base_name, x, y, z, nbt

    @abstractmethod
    def encode(self, *args, **kwargs) -> Any:
        """
        Take a version-specific chunk and encode it to raw data for the format to store.
        """
        raise NotImplementedError

    def _encode_entity(
        self, entity: Entity, id_type: EntityIDType, coord_type: EntityCoordType
    ) -> Optional[amulet_nbt.NBTFile]:
        return self._encode_base_entity(entity, id_type, coord_type)

    def _encode_block_entity(
        self, entity: BlockEntity, id_type: EntityIDType, coord_type: EntityCoordType
    ) -> Optional[amulet_nbt.NBTFile]:
        return self._encode_base_entity(entity, id_type, coord_type)

    @staticmethod
    def _encode_base_entity(
        entity: Union[Entity, BlockEntity],
        id_type: EntityIDType,
        coord_type: EntityCoordType,
    ) -> Optional[amulet_nbt.NBTFile]:
        if not isinstance(entity.nbt, amulet_nbt.NBTFile) and isinstance(
            entity.nbt.value, amulet_nbt.TAG_Compound
        ):
            return
        nbt = entity.nbt

        if id_type == EntityIDType.namespace_str_id:
            nbt["id"] = amulet_nbt.TAG_String(entity.namespaced_name)
        elif id_type == EntityIDType.namespace_str_Id:
            nbt["Id"] = amulet_nbt.TAG_String(entity.namespaced_name)
        elif id_type == EntityIDType.namespace_str_identifier:
            nbt["identifier"] = amulet_nbt.TAG_String(entity.namespaced_name)
        elif id_type == EntityIDType.str_id:
            nbt["id"] = amulet_nbt.TAG_String(entity.base_name)
        elif id_type == EntityIDType.int_id:
            if not entity.base_name.isnumeric():
                return
            nbt["id"] = amulet_nbt.TAG_Int(int(entity.base_name))
        else:
            raise NotImplementedError(f"Entity id type {id_type}")

        if coord_type == EntityCoordType.Pos_list_double:
            nbt["Pos"] = amulet_nbt.TAG_List(
                [
                    amulet_nbt.TAG_Double(float(entity.x)),
                    amulet_nbt.TAG_Double(float(entity.y)),
                    amulet_nbt.TAG_Double(float(entity.z)),
                ]
            )
        elif coord_type == EntityCoordType.Pos_list_float:
            nbt["Pos"] = amulet_nbt.TAG_List(
                [
                    amulet_nbt.TAG_Float(float(entity.x)),
                    amulet_nbt.TAG_Float(float(entity.y)),
                    amulet_nbt.TAG_Float(float(entity.z)),
                ]
            )
        elif coord_type == EntityCoordType.Pos_list_int:
            nbt["Pos"] = amulet_nbt.TAG_List(
                [
                    amulet_nbt.TAG_Int(int(entity.x)),
                    amulet_nbt.TAG_Int(int(entity.y)),
                    amulet_nbt.TAG_Int(int(entity.z)),
                ]
            )
        elif coord_type == EntityCoordType.Pos_array_int:
            nbt["Pos"] = amulet_nbt.TAG_Int_Array(
                [int(entity.x), int(entity.y), int(entity.z)]
            )
        elif coord_type == EntityCoordType.xyz_int:
            nbt["x"] = amulet_nbt.TAG_Int(int(entity.x))
            nbt["y"] = amulet_nbt.TAG_Int(int(entity.y))
            nbt["z"] = amulet_nbt.TAG_Int(int(entity.z))
        else:
            raise NotImplementedError(f"Entity coord type {coord_type}")

        return nbt

    @overload
    @staticmethod
    def check_type(obj: TAG_Compound, key: str, dtype: Type[AnyNBT]) -> bool:
        ...

    @overload
    @staticmethod
    def check_type(obj: TAG_List, key: int, dtype: Type[AnyNBT]) -> bool:
        ...

    @staticmethod
    def check_type(
        obj: Union[TAG_Compound, TAG_List], key: Union[str, int], dtype: Type[AnyNBT]
    ) -> bool:
        """Check the key exists and the type is correct."""
        return key in obj and isinstance(obj[key], dtype)

    @overload
    def get_obj(
        self,
        obj: TAG_Compound,
        key: str,
        dtype: Type[AnyNBT],
        default: Optional[AnyNBT] = None,
    ) -> Optional[AnyNBT]:
        ...

    @overload
    def get_obj(
        self,
        obj: TAG_List,
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

        :param obj: The TAG_Compound to read from.
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

    @staticmethod
    def set_obj(
        obj: TAG_Compound,
        key: str,
        dtype: Type[AnyNBT],
        default: Optional[AnyNBT] = None,
    ) -> AnyNBT:
        """Set a key in a compound tag if the key does not exist or is not the correct type.
        This works in much the same way as dict.setdefault but overwrites if the data type does not match.

        :param obj: The TAG_Compound to apply to.
        :param key: The key to use.
        :param dtype: The expected data type.
        :param default: The default value to use if the existing is not valid. If None will use dtype()
        :return: The final value in the key.
        """
        if key not in obj or not isinstance(obj[key], dtype):
            if default is None:
                obj[key] = dtype()
            else:
                assert isinstance(default, dtype)
                obj[key] = default
        return obj[key]

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
