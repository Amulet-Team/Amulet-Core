from unittest import TestCase
import os

from amulet.block import BlockStack
from amulet.biome import Biome
from amulet.chunk import ChunkDoesNotExist
from amulet.selection import SelectionBox
from amulet.utils.lock import OrderedLock
from amulet.level.java import JavaRawLevel, JavaRawDimension
from amulet_nbt import NamedTag

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp


class JavaRawDimensionTestCase(TestCase):
    def test_dimension(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)
            raw_level.open()
            try:
                overworld = raw_level.get_dimension("minecraft:overworld")
                nether = raw_level.get_dimension("minecraft:the_nether")

                for dimension in (overworld, nether):
                    self.assertIsInstance(dimension, JavaRawDimension)
                    self.assertIsInstance(dimension.lock, OrderedLock)
                    self.assertIsInstance(dimension.default_block, BlockStack)
                    self.assertIsInstance(dimension.default_biome, Biome)
                    self.assertIsInstance(dimension.bounds, SelectionBox)

                self.assertEqual("", overworld.relative_path)
                self.assertEqual("minecraft:overworld", overworld.dimension_id)
                self.assertEqual(1089, len(list(overworld.all_chunk_coords)))
                self.assertEqual("DIM-1", nether.relative_path)
                self.assertEqual("minecraft:the_nether", nether.dimension_id)
                self.assertEqual(0, len(list(nether.all_chunk_coords)))

                self.assertFalse(overworld.is_destroyed())
                self.assertFalse(nether.is_destroyed())
            finally:
                raw_level.close()

            self.assertTrue(overworld.is_destroyed())
            self.assertTrue(nether.is_destroyed())

    def test_edit(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)
            raw_level.open()
            try:
                overworld = raw_level.get_dimension("minecraft:overworld")
                self.assertTrue(overworld.has_chunk(0, 0))

                # Get chunk data
                chunk_data = overworld.get_raw_chunk(0, 0)
                self.assertIsInstance(chunk_data, dict)
                self.assertTrue(chunk_data)
                for k, v in chunk_data.items():
                    self.assertIsInstance(k, str)
                    self.assertIsInstance(v, NamedTag)

                # Delete chunk
                overworld.delete_chunk(0, 0)
                self.assertFalse(overworld.has_chunk(0, 0))
                # Should be able to delete chunks that don't exist.
                overworld.delete_chunk(0, 0)
                self.assertFalse(overworld.has_chunk(0, 0))

                # Try getting
                with self.assertRaises(ChunkDoesNotExist):
                    overworld.get_raw_chunk(0, 0)

                # Write back
                overworld.set_raw_chunk(0, 0, chunk_data)
                self.assertTrue(overworld.has_chunk(0, 0))
                self.assertEqual(chunk_data, overworld.get_raw_chunk(0, 0))
            finally:
                raw_level.close()

    def test_compact(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:

            def get_region_size() -> int:
                return sum(
                    entry.stat().st_size
                    for entry in os.scandir(
                        os.path.join(world_data.temp_path, "region")
                    )
                    if entry.is_file()
                )

            raw_level = JavaRawLevel.load(world_data.temp_path)
            raw_level.open()
            try:
                overworld = raw_level.get_dimension("minecraft:overworld")
                self.assertTrue(overworld.has_chunk(0, 0))

                # Clear any unused space and get the size.
                overworld.compact()
                start_size = get_region_size()

                # Get chunk data
                chunk_data = overworld.get_raw_chunk(0, 0)

                # Delete chunk
                overworld.delete_chunk(0, 0)
                self.assertFalse(overworld.has_chunk(0, 0))
                # Deleting should not resize the region files.
                self.assertEqual(get_region_size(), start_size)

                # Compact to remove the deleted chunk's space
                overworld.compact()
                compacted_size = get_region_size()
                self.assertLess(compacted_size, start_size)

                # Write back
                overworld.set_raw_chunk(0, 0, chunk_data)
                self.assertTrue(overworld.has_chunk(0, 0))
                self.assertEqual(chunk_data, overworld.get_raw_chunk(0, 0))
            finally:
                raw_level.close()

            # This stat isn't updated until the files are flushed. Closing does that.
            self.assertGreater(get_region_size(), compacted_size)
