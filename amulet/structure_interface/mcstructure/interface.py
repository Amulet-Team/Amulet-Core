from typing import TYPE_CHECKING, Any, Tuple, Union, Optional, List
import numpy

import amulet_nbt

from amulet.api.wrapper import Interface
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionBox
from amulet.api.data_types import AnyNDArray
from amulet.world_interface.chunk import translators
from amulet.api.block import Block
from .mcstructure import MCStructureChunk

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from PyMCTranslate import TranslationManager


class MCStructureInterface(Interface):
    _entity_id_type = "namespace-str-identifier"
    _entity_coord_type = "Pos-list-float"
    _block_entity_id_type = "str-id"
    _block_entity_coord_type = "xyz-int"

    def is_valid(self, key: Tuple) -> bool:
        return True

    def decode(
        self, cx: int, cz: int, section: MCStructureChunk
    ) -> Tuple["Chunk", AnyNDArray]:
        palette = numpy.empty(len(section.palette) + 1, dtype=numpy.object)
        palette[0] = (
            (
                17563649,
                Block(
                    namespace="minecraft",
                    base_name="air",
                    properties={"block_data": amulet_nbt.TAG_Int(0)},
                ),
            ),
        )

        for index, blocks in enumerate(section.palette):
            block_layers: List[Tuple[Optional[int], Block]] = []
            for block in blocks:
                namespace, base_name = block["name"].value.split(":", 1)
                if "version" in block:
                    version: Optional[int] = block["version"].value
                else:
                    version = None

                if "states" in block:  # 1.13 format
                    properties = block["states"].value
                    if version is None:
                        version = 17694720  # 1, 14, 0, 0
                else:
                    properties = {"block_data": amulet_nbt.TAG_Int(block["val"].value)}
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
        box = section.selection.create_moved_box((cx * 16, 0, cz * 16), subtract=True)
        chunk.blocks[box.slice] = section.blocks + 1
        for b in section.block_entities:
            b = self._decode_block_entity(
                b, self._block_entity_id_type, self._block_entity_coord_type
            )
            if b is not None:
                chunk.block_entities.insert(b)
        for b in section.entities:
            b = self._decode_entity(
                b, self._block_entity_id_type, self._block_entity_coord_type
            )
            if b is not None:
                chunk.entities.append(b)

        return chunk, palette

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        box: SelectionBox = None,
    ) -> MCStructureChunk:
        entities = []
        for e in chunk.entities:
            if e.location in box:
                entities.append(
                    self._encode_entity(
                        e, self._entity_id_type, self._entity_coord_type
                    ).value
                )
        block_entities = []
        for e in chunk.block_entities:
            if e.location in box:
                block_entities.append(
                    self._encode_block_entity(
                        e, self._block_entity_id_type, self._block_entity_coord_type
                    ).value
                )

        slices = box.create_moved_box(
            (chunk.cx * 16, 0, chunk.cz * 16), subtract=True
        ).slice

        out_palette = numpy.empty(palette.shape, dtype=object)
        for index, block_layers in enumerate(palette):
            blocks_out = []
            for version, block in block_layers:
                block = amulet_nbt.TAG_Compound(
                    {
                        "name": amulet_nbt.TAG_String(
                            f"{block.namespace}:{block.base_name}"
                        ),
                        "states": amulet_nbt.TAG_Compound(block.properties),
                    }
                )
                if version:
                    block["version"] = amulet_nbt.TAG_Int(version)
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
        max_world_version: Tuple[str, Tuple[int, int, int]],
        data: Any = None,
        translation_manager: "TranslationManager" = None,
    ) -> Tuple["Translator", Union[int, Tuple[int, int, int]]]:
        platform, version_number = max_world_version
        if platform == "java":
            version = translation_manager.get_version(platform, version_number)
            version_number = version.data_version
        return translators.loader.get((platform, version_number)), version_number
