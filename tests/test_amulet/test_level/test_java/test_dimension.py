from unittest import TestCase

from amulet.block import BlockStack
from amulet.biome import Biome
from amulet.selection import SelectionBox
from amulet.level.java import (
    JavaLevel,
    JavaDimension,
    JavaChunkHandle,
)

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp


class JavaDimensionTestCase(TestCase):
    def test_dimension(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.open()
            try:
                overworld = level.get_dimension("minecraft:overworld")
                self.assertIsInstance(overworld, JavaDimension)
                self.assertEqual("minecraft:overworld", overworld.dimension_id)
                self.assertIsInstance(overworld.bounds, SelectionBox)
                self.assertEqual(
                    SelectionBox(
                        -30_000_000, 0, -30_000_000, 60_000_000, 256, 60_000_000
                    ),
                    overworld.bounds,
                )
                self.assertIsInstance(overworld.default_block, BlockStack)
                self.assertIsInstance(overworld.default_biome, Biome)
                self.assertIsInstance(overworld.get_chunk_handle(0, 0), JavaChunkHandle)

            finally:
                level.close()
