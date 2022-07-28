from typing import TYPE_CHECKING, Any, Tuple, Optional, List
import numpy

from amulet_nbt import IntTag, StringTag, CompoundTag

from amulet.api.wrapper import Interface, EntityIDType, EntityCoordType
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionBox
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberTuple,
    VersionIdentifierType,
    VersionNumberAny,
    PlatformType,
)
from amulet.level.loader import Translators
from amulet.api.block import Block
from .chunk import MCStructureChunk

from amulet_nbt import NamedTag

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from PyMCTranslate import TranslationManager


class MCStructureInterface(Interface):
    _entity_id_type = EntityIDType.namespace_str_identifier
    _entity_coord_type = EntityCoordType.Pos_list_float
    _block_entity_id_type = EntityIDType.str_id
    _block_entity_coord_type = EntityCoordType.xyz_int

    def is_valid(self, key: Tuple) -> bool:
        return True

    def decode(
        self, cx: int, cz: int, data: MCStructureChunk
    ) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: Raw chunk data provided by the format.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        palette = numpy.empty(len(data.palette) + 1, dtype=object)
        palette[0] = (
            (
                17563649,
                Block(
                    namespace="minecraft",
                    base_name="air",
                    properties={"block_data": IntTag(0)},
                ),
            ),
        )

        for index, blocks in enumerate(data.palette):
            block_layers: List[Tuple[Optional[int], Block]] = []
            for block in blocks:
                namespace, base_name = block["name"].py_str.split(":", 1)
                if "version" in block:
                    version: Optional[int] = block["version"].py_int
                else:
                    version = None

                if "states" in block:  # 1.13 format
                    properties = block["states"].py_dict
                    if version is None:
                        version = 17694720  # 1, 14, 0, 0
                else:
                    properties = {"block_data": IntTag(block["val"].py_int)}
                block_layers.append(
                    (
                        version,
                        Block(
                            namespace=namespace,
                            base_name=base_name,
                            properties=properties,
                        ),
                    )
                )
            palette[index + 1] = block_layers

        chunk = Chunk(cx, cz)
        box = data.selection.create_moved_box((cx * 16, 0, cz * 16), subtract=True)
        chunk.blocks[box.slice] = data.blocks + 1
        for tag in data.block_entities:
            block_entity = self._decode_block_entity(
                NamedTag(tag), self._block_entity_id_type, self._block_entity_coord_type
            )
            if block_entity is not None:
                chunk.block_entities.insert(block_entity)
        for tag in data.entities:
            entity = self._decode_entity(
                NamedTag(tag), self._block_entity_id_type, self._block_entity_coord_type
            )
            if entity is not None:
                chunk.entities.append(entity)

        return chunk, palette

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: VersionIdentifierType,
        box: SelectionBox,
    ) -> MCStructureChunk:
        """
        Take a version-specific chunk and encode it to raw data for the format to store.
        :param chunk: The already translated version-specfic chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param box: The volume of the chunk to pack.
        :return: Raw data to be stored by the Format.
        """
        entities = []
        for entity in chunk.entities:
            if entity.location in box:
                entities.append(
                    self._encode_entity(
                        entity, self._entity_id_type, self._entity_coord_type
                    ).compound
                )
        block_entities = []
        for block_entity in chunk.block_entities:
            if block_entity.location in box:
                block_entities.append(
                    self._encode_block_entity(
                        block_entity,
                        self._block_entity_id_type,
                        self._block_entity_coord_type,
                    ).compound
                )

        slices = box.create_moved_box(
            (chunk.cx * 16, 0, chunk.cz * 16), subtract=True
        ).slice

        out_palette = numpy.empty(palette.shape, dtype=object)
        for index, block_layers in enumerate(palette):
            blocks_out = []
            for version, block in block_layers:
                block = CompoundTag(
                    {
                        "name": StringTag(f"{block.namespace}:{block.base_name}"),
                        "states": CompoundTag(block.properties),
                    }
                )
                if version:
                    block["version"] = IntTag(version)
                blocks_out.append(block)
            out_palette[index] = blocks_out

        return MCStructureChunk(
            box,
            numpy.asarray(chunk.blocks[slices]),
            out_palette,
            block_entities,
            entities,
        )

    def get_translator(
        self,
        max_world_version: Tuple[PlatformType, VersionNumberTuple],
        data: Any = None,
        translation_manager: "TranslationManager" = None,
    ) -> Tuple["Translator", VersionNumberAny]:
        platform, version_number = max_world_version
        if platform != "bedrock":
            raise ValueError("Platform must be bedrock")
        return Translators.get((platform, version_number)), version_number
