from typing import TYPE_CHECKING, Any, Tuple, List
import numpy

from amulet_nbt import IntTag
from amulet.api.wrapper import Interface
from .section import ConstructionSection
from amulet.api.chunk import Chunk
from amulet.api.block import Block
from amulet.api.selection import SelectionBox
from amulet.level.loader import Translators
from amulet.api.data_types import (
    AnyNDArray,
    PlatformType,
    VersionNumberTuple,
    VersionIdentifierType,
    VersionNumberAny,
)

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from PyMCTranslate import TranslationManager


class ConstructionInterface(Interface):
    def is_valid(self, key: Tuple) -> bool:
        return key[0] == "construction" and key[1] == 0

    def decode(
        self, cx: int, cz: int, data: List[ConstructionSection]
    ) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: Raw chunk data provided by the format.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        chunk = Chunk(cx, cz)
        palette = []
        for section in data:
            if any(s == 0 for s in section.shape):
                continue
            if section.blocks is not None:
                shapex, shapey, shapez = section.shape
                sx = section.sx % 16
                sy = section.sy
                sz = section.sz % 16
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
                properties={"block_data": IntTag(0)},
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
        max_world_version: VersionIdentifierType,
        boxes: List[SelectionBox],
    ) -> List[ConstructionSection]:
        """
        Take a version-specific chunk and encode it to raw data for the format to store.
        :param chunk: The already translated version-specfic chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param boxes: The volume(s) of the chunk to pack.
        :return: Raw data to be stored by the Format.
        """
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
        max_world_version: Tuple[PlatformType, VersionNumberTuple],
        data: Any = None,
        translation_manager: "TranslationManager" = None,
    ) -> Tuple["Translator", VersionNumberAny]:
        platform, version_number = max_world_version
        version = translation_manager.get_version(platform, version_number)
        if platform == "java":
            version_number = version.data_version
        return Translators.get((platform, version_number)), version_number


class Construction0Interface(ConstructionInterface):
    pass
