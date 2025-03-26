from unittest import TestCase

from amulet.utils.lock import OrderedLock
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

                exists_chunk_handle = overworld.get_chunk_handle(1, 2)
                self.assertIsInstance(exists_chunk_handle, JavaChunkHandle)

                self.assertIsInstance(exists_chunk_handle.lock, OrderedLock)

                self.assertIsInstance(exists_chunk_handle.dimension_id, str)
                self.assertEqual("minecraft:overworld", exists_chunk_handle.dimension_id)

                self.assertIsInstance(exists_chunk_handle.cx, int)
                self.assertEqual(1, exists_chunk_handle.cx)

                self.assertIsInstance(exists_chunk_handle.cz, int)
                self.assertEqual(2, exists_chunk_handle.cz)

                self.assertTrue(exists_chunk_handle.exists())

                does_not_exist_chunk_handle = overworld.get_chunk_handle(100, 200)
                self.assertIsInstance(does_not_exist_chunk_handle, JavaChunkHandle)

                self.assertIsInstance(does_not_exist_chunk_handle.lock, OrderedLock)

                self.assertIsInstance(does_not_exist_chunk_handle.dimension_id, str)
                self.assertEqual("minecraft:overworld", does_not_exist_chunk_handle.dimension_id)

                self.assertIsInstance(does_not_exist_chunk_handle.cx, int)
                self.assertEqual(100, does_not_exist_chunk_handle.cx)

                self.assertIsInstance(does_not_exist_chunk_handle.cz, int)
                self.assertEqual(200, does_not_exist_chunk_handle.cz)

                self.assertFalse(does_not_exist_chunk_handle.exists())

            finally:
                level.close()
