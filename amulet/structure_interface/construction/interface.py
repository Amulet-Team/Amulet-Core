from typing import TYPE_CHECKING, Any, Tuple, Union, List
import numpy

import amulet_nbt
from amulet.api.wrapper import Interface
from .construction import ConstructionSection
from amulet.api.chunk import Chunk
from amulet.api.block import Block
from amulet.api.selection import SelectionBox
from amulet.world_interface.chunk import translators
from amulet.api.data_types import AnyNDArray

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from PyMCTranslate import TranslationManager


class ConstructionInterface(Interface):
    def is_valid(self, key: Tuple) -> bool:
        return True

    def decode(
        self, cx: int, cz: int, data: List[ConstructionSection]
    ) -> Tuple["Chunk", AnyNDArray]:
        chunk = Chunk(cx, cz)
        palette = []
        for section in data:
            if any(s == 0 for s in section.shape):
                continue
            if section.blocks is not None:
                shapex, shapey, shapez = section.shape
                sx = section.sx - ((section.sx >> 4) << 4)
                sy = section.sy
                sz = section.sz - ((section.sz >> 4) << 4)
                chunk.blocks[
                    sx : sx + shapex,
                    sy : sy + shapey,
                    sz : sz + shapez,
                ] = section.blocks.astype(numpy.uint32) + len(palette)
                chunk.block_entities.update(section.block_entities)
            chunk.entities.extend(section.entities)
            palette += section.palette

        np_palette, inverse = numpy.unique(palette, return_inverse=True)
        np_palette = numpy.insert(
            np_palette,
            0,
            Block(
                namespace="minecraft",
                base_name="air",
                properties={"block_data": amulet_nbt.TAG_Int(0)},
            ),
        )
        inverse += 1
        np_palette: AnyNDArray
        inverse: numpy.ndarray
        for cy in chunk.blocks.sub_chunks:
            chunk.blocks.add_sub_chunk(
                cy, inverse[chunk.blocks.get_sub_chunk(cy)].astype(numpy.uint32)
            )
        return chunk, np_palette

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        boxes: List[SelectionBox] = None,
    ) -> List[ConstructionSection]:
        sections = []
        for box in boxes:
            cx, cz = chunk.cx, chunk.cz
            for cy in box.chunk_y_locations():
                sub_box = box.intersection(
                    SelectionBox.create_sub_chunk_box(cx, cy, cz)
                )
                entities = [e for e in chunk.entities if e.location in sub_box]
                if cy in chunk.blocks:
                    sections.append(
                        ConstructionSection(
                            sub_box.min,
                            sub_box.shape,
                            numpy.asarray(chunk.blocks[sub_box.chunk_slice(cx, cz)]),
                            list(palette),
                            entities,
                            [e for e in chunk.block_entities if e.location in sub_box],
                        )
                    )
                elif entities:
                    sections.append(
                        ConstructionSection(
                            sub_box.min, sub_box.shape, None, [], entities, []
                        )
                    )

        return sections

    def get_translator(
        self,
        max_world_version: Tuple[str, Tuple[int, int, int]],
        data: Any = None,
        translation_manager: "TranslationManager" = None,
    ) -> Tuple["Translator", Union[int, Tuple[int, int, int]]]:
        platform, version_number = max_world_version
        version = translation_manager.get_version(platform, version_number)
        if platform == "java":
            version_number = version.data_version
        return translators.loader.get((platform, version_number)), version_number


class Construction0Interface(ConstructionInterface):
    pass
