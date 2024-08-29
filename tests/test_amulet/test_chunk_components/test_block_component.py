from unittest import TestCase
from amulet.chunk import Chunk
from amulet.chunk_components import BlockComponent, BlockComponentData, SectionArrayMap
from amulet.palette import BlockPalette
from .test_component import test_component


def test_block_component(self: TestCase, chunk: Chunk):
    self.assertIsInstance(chunk, BlockComponent)
    self.assertIsInstance(chunk.block, BlockComponentData)
    self.assertIsInstance(chunk.block.palette, BlockPalette)
    self.assertIsInstance(chunk.block.sections, SectionArrayMap)


class TestBlockComponent(TestCase):
    def test_block_component(self) -> None:
        test_component(self, BlockComponent)
