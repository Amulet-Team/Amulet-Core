from unittest import TestCase
from amulet.core.chunk import Chunk
from amulet.core.chunk.component import BlockComponent, BlockComponentData, SectionArrayMap
from amulet.core.palette import BlockPalette
from test_amulet_core.test_chunk_components.test_component import test_component


def test_block_component(self: TestCase, chunk: Chunk) -> None:
    self.assertIsInstance(chunk, BlockComponent)
    assert isinstance(chunk, BlockComponent)
    self.assertIsInstance(chunk.block, BlockComponentData)
    self.assertIsInstance(chunk.block.palette, BlockPalette)
    self.assertIsInstance(chunk.block.sections, SectionArrayMap)


class TestBlockComponent(TestCase):
    def test_block_component(self) -> None:
        test_component(self, BlockComponent)
