from __future__ import annotations

import numpy
from typing import Tuple, Any, Union, TYPE_CHECKING, Optional

from amulet.api.block_entity import BlockEntity
from amulet.api.entity import Entity
from amulet.api.data_types import AnyNDArray
import amulet_nbt

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from amulet.api.chunk import Chunk


class Interface:
    def decode(self, cx: int, cz: int, data: Any) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format
        :param cx: chunk x coordinate
        :type cx: int
        :param cz: chunk z coordinate
        :type cz: int
        :param data: Raw chunk data provided by the format.
        :type data: Any
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        :rtype: Chunk
        """
        raise NotImplementedError()

    def _decode_entity(
        self, nbt: amulet_nbt.NBTFile, id_type: str, coord_type: str
    ) -> Optional[Entity]:
        entity = self._decode_base_entity(nbt, id_type, coord_type)
        if entity is not None:
            namespace, base_name, x, y, z, nbt = entity
            return Entity(
                namespace=namespace, base_name=base_name, x=x, y=y, z=z, nbt=nbt
            )

    def _decode_block_entity(
        self, nbt: amulet_nbt.NBTFile, id_type: str, coord_type: str
    ) -> Optional[BlockEntity]:
        entity = self._decode_base_entity(nbt, id_type, coord_type)
        if entity is not None:
            namespace, base_name, x, y, z, nbt = entity
            return BlockEntity(
                namespace=namespace, base_name=base_name, x=x, y=y, z=z, nbt=nbt
            )

    @staticmethod
    def _decode_base_entity(
        nbt: amulet_nbt.NBTFile, id_type: str, coord_type: str
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
        if not isinstance(nbt, amulet_nbt.NBTFile) and isinstance(
            nbt.value, amulet_nbt.TAG_Compound
        ):
            return

        if id_type == "namespace-str-id":
            entity_id = nbt.pop("id", amulet_nbt.TAG_String(""))
            if (
                not isinstance(entity_id, amulet_nbt.TAG_String)
                or entity_id.value == ""
                or ":" not in entity_id.value
            ):
                return
            namespace, base_name = entity_id.value.split(":", 1)

        elif id_type == "str-id":
            entity_id = nbt.pop("id", amulet_nbt.TAG_String(""))
            if (
                not isinstance(entity_id, amulet_nbt.TAG_String)
                or entity_id.value == ""
            ):
                return
            namespace = ""
            base_name = entity_id.value

        elif id_type in ["namespace-str-identifier", "int-id"]:
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

        if coord_type in ["Pos-list-double", "Pos-list-float"]:
            if "Pos" not in nbt:
                return
            pos = nbt.pop("Pos")
            pos: amulet_nbt.TAG_List
            if not (5 <= pos.list_data_type <= 6 and len(pos) == 3):
                return
            x, y, z = [c.value for c in pos]
        elif coord_type == "xyz-int":
            if not all(
                c in nbt and isinstance(nbt[c], amulet_nbt.TAG_Int)
                for c in ("x", "y", "z")
            ):
                return
            x, y, z = [nbt.pop(c).value for c in ("x", "y", "z")]
        else:
            raise NotImplementedError(f"Entity coord type {coord_type}")

        return namespace, base_name, x, y, z, nbt

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
    ) -> Any:
        """
        Take a version-specific chunk and encode it to raw data for the format to store.
        :param chunk: The already translated version-specfic chunk to encode.
        :type chunk: Chunk
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :type max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]]
        :return: Raw data to be stored by the Format.
        :rtype: Any
        """
        raise NotImplementedError()

    def _encode_entity(
        self, entity: Entity, id_type: str, coord_type: str
    ) -> Optional[amulet_nbt.NBTFile]:
        return self._encode_base_entity(entity, id_type, coord_type)

    def _encode_block_entity(
        self, entity: BlockEntity, id_type: str, coord_type: str
    ) -> Optional[amulet_nbt.NBTFile]:
        return self._encode_base_entity(entity, id_type, coord_type)

    @staticmethod
    def _encode_base_entity(
        entity: Union[Entity, BlockEntity], id_type: str, coord_type: str
    ) -> Optional[amulet_nbt.NBTFile]:
        if not isinstance(entity.nbt, amulet_nbt.NBTFile) and isinstance(
            entity.nbt.value, amulet_nbt.TAG_Compound
        ):
            return
        nbt = entity.nbt

        if id_type == "namespace-str-id":
            nbt["id"] = amulet_nbt.TAG_String(entity.namespaced_name)
        elif id_type == "namespace-str-identifier":
            nbt["identifier"] = amulet_nbt.TAG_String(entity.namespaced_name)
        elif id_type == "str-id":
            nbt["id"] = amulet_nbt.TAG_String(entity.base_name)
        elif id_type == "int-id":
            if not entity.base_name.isnumeric():
                return
            nbt["id"] = amulet_nbt.TAG_Int(int(entity.base_name))
        else:
            raise NotImplementedError(f"Entity id type {id_type}")

        if coord_type == "Pos-list-double":
            nbt["Pos"] = amulet_nbt.TAG_List(
                [
                    amulet_nbt.TAG_Double(float(entity.x)),
                    amulet_nbt.TAG_Double(float(entity.y)),
                    amulet_nbt.TAG_Double(float(entity.z)),
                ]
            )
        elif coord_type == "Pos-list-float":
            nbt["Pos"] = amulet_nbt.TAG_List(
                [
                    amulet_nbt.TAG_Float(float(entity.x)),
                    amulet_nbt.TAG_Float(float(entity.y)),
                    amulet_nbt.TAG_Float(float(entity.z)),
                ]
            )
        elif coord_type == "xyz-int":
            nbt["x"] = amulet_nbt.TAG_Int(int(entity.x))
            nbt["y"] = amulet_nbt.TAG_Int(int(entity.y))
            nbt["z"] = amulet_nbt.TAG_Int(int(entity.z))
        else:
            raise NotImplementedError(f"Entity coord type {coord_type}")

        return nbt

    def get_translator(
        self,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        data: Any = None,
    ) -> Tuple["Translator", Union[int, Tuple[int, int, int]]]:
        """
        Get the Translator class for the requested version.
        :param max_world_version: The game version the world was last opened in.
        :type max_world_version: Java: int (DataVersion)    Bedrock: Tuple[int, int, int, ...] (game version number)
        :param data: Optional data to get translator based on chunk version rather than world version
        :param data: Any
        :return: Tuple[Translator, version number for PyMCTranslate to use]
        :rtype: Tuple[Translator, Union[int, Tuple[int, int, int]]]
        """
        raise NotImplementedError

    @staticmethod
    def is_valid(key: Tuple) -> bool:
        """
        Returns whether this Interface is able to interface with the chunk type with a given identifier key,
        generated by the format.

        :param key: The key who's decodability needs to be checked.
        :return: True if this interface can interface with the chunk version associated with the key, False otherwise.
        """
        raise NotImplementedError()
