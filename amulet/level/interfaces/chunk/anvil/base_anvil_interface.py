from __future__ import annotations
from abc import abstractmethod

from typing import List, Tuple, Iterable, TYPE_CHECKING, Any
import numpy


from amulet_nbt import (
    TAG_Int,
    TAG_List,
    TAG_Compound,
    NBTFile,
)

from amulet.api.chunk import Chunk, StatusFormats
from amulet.api.wrapper import Interface
from amulet.level import loader
from amulet.api.data_types import AnyNDArray, VersionIdentifierType
from amulet.api.wrapper import EntityIDType, EntityCoordType

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity


class BaseAnvilInterface(Interface):
    def __init__(self):
        self._feature_options = {
            "status": StatusFormats,
            "height_map": [
                "256IARequired",  # A 256 element Int Array in HeightMap
                "256IA",  # A 256 element Int Array in HeightMap
                "C|V1",  # A Compound of Long Arrays with these keys "LIQUID", "SOLID", "LIGHT", "RAIN"
                "C|V2",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING"
                "C|V3",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING", "WORLD_SURFACE"
                "C|V4",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "WORLD_SURFACE"
            ],
            # 'carving_masks': ['C|?BA'],
            "light_optional": ["false", "true"],
            "block_entity_format": [EntityIDType.namespace_str_id],
            "block_entity_coord_format": [EntityCoordType.xyz_int],
            "entity_format": [EntityIDType.namespace_str_id],
            "entity_coord_format": [EntityCoordType.Pos_list_double],
            # 'lights': [],
        }
        self._features = {key: None for key in self._feature_options.keys()}

    def _set_feature(self, feature: str, option: Any):
        assert feature in self._feature_options, f"{feature} is not a valid feature."
        assert (
            option is None or option in self._feature_options[feature]
        ), f'Invalid option {option} for feature "{feature}"'
        self._features[feature] = option

    def is_valid(self, key: Tuple) -> bool:
        return key[0] == "java" and self.minor_is_valid(key[1])

    @staticmethod
    @abstractmethod
    def minor_is_valid(key: int):
        raise NotImplementedError

    def get_translator(
        self,
        max_world_version: VersionIdentifierType,
        data: NBTFile = None,
    ) -> Tuple["Translator", int]:
        if data:
            data_version = data.get("DataVersion", TAG_Int(-1)).value
            key, version = (("java", data_version), data_version)
        else:
            key = max_world_version
            version = max_world_version[1]
        return loader.Translators.get(key), version

    @abstractmethod
    def decode(
        self, cx: int, cz: int, nbt_file: NBTFile, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data.
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param nbt_file: NBTFile
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        raise NotImplementedError

    def _decode_entity_list(self, entities: TAG_List) -> List["Entity"]:
        entities_out = []
        if entities.list_data_type == TAG_Compound.tag_id:
            for nbt in entities:
                entity = self._decode_entity(
                    NBTFile(nbt),
                    self._features["entity_format"],
                    self._features["entity_coord_format"],
                )
                if entity is not None:
                    entities_out.append(entity)

        return entities_out

    def _decode_block_entity_list(
        self, block_entities: TAG_List
    ) -> List["BlockEntity"]:
        entities_out = []
        if block_entities.list_data_type == TAG_Compound.tag_id:
            for nbt in block_entities:
                if not isinstance(nbt, TAG_Compound):
                    continue
                entity = self._decode_block_entity(
                    NBTFile(nbt),
                    self._features["block_entity_format"],
                    self._features["block_entity_coord_format"],
                )
                if entity is not None:
                    entities_out.append(entity)

        return entities_out

    @abstractmethod
    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, int],
        bounds: Tuple[int, int],
    ) -> NBTFile:
        """
        Encode a version-specific chunk to raw data for the format to store.

        :param chunk: The already translated version-specific chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Raw data to be stored by the Format.
        """
        raise NotImplementedError

    def _encode_entity_list(self, entities: Iterable["Entity"]) -> TAG_List:
        entities_out = []
        for entity in entities:
            nbt = self._encode_entity(
                entity,
                self._features["entity_format"],
                self._features["entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.value)

        return TAG_List(entities_out)

    def _encode_block_entity_list(
        self, block_entities: Iterable["BlockEntity"]
    ) -> TAG_List:
        entities_out = []
        for entity in block_entities:
            nbt = self._encode_block_entity(
                entity,
                self._features["block_entity_format"],
                self._features["block_entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.value)

        return TAG_List(entities_out)
