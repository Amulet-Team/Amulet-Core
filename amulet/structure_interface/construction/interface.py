from typing import TYPE_CHECKING, Any, Tuple, Union, List
import numpy

from amulet.api.wrapper import Interface
from .construction import ConstructionSection
from amulet.api.chunk import Chunk
from amulet.api.block import Block

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator


class ConstructionInterface(Interface):
    def decode(self, cx: int, cz: int, data: List[ConstructionSection]) -> Tuple['Chunk', numpy.ndarray]:
        chunk = Chunk(cx, cz)
        palette = [Block(namespace="minecraft", base_name="air")]
        for section in data:
            shapex, shapey, shapez = section.shape
            sx = section.sx % 16
            sy = section.sy % 16
            sz = section.sz % 16
            chunk.blocks[
                sx: sx + shapex,
                sy: sy + shapey,
                sz: sz + shapez,
            ] = section.blocks + len(palette)
            chunk.entities.extend(section.entities)
            chunk.block_entities.update(section.block_entities)

        np_palette, inverse = numpy.unique(palette, return_inverse=True)
        np_palette: numpy.ndarray
        inverse: numpy.ndarray
        for cy in chunk.blocks:
            chunk.blocks.add_sub_chunk(
                cy,
                inverse[chunk.blocks.get_sub_chunk(cy)].astype(numpy.uint32)
            )
        return chunk, np_palette

    def encode(
        self,
        chunk: 'Chunk',
        palette: numpy.ndarray,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        boxes: List[Tuple[int, int, int, int, int, int]]
    ) -> List[ConstructionSection]:
        pass

    def get_translator(
        self,
        max_world_version: Tuple[str, Tuple[int, int, int]],
        data: Any = None,
    ) -> Tuple['Translator', Union[int, Tuple[int, int, int]]]:
        # TODO: handle converting to dataversion for Java
        pass


class Construction0Interface(ConstructionInterface):
    pass
